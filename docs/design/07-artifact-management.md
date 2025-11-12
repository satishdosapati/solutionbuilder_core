# Design Document: Artifact Management

**Version:** 1.0  
**Status:** Ready for Implementation  
**Last Updated:** 2024-01-XX  
**Depends on:** 01-core-platform-architecture.md, 05-implement-mode.md

## Overview

This document defines the artifact management system for storing, organizing, and downloading generated infrastructure code and documentation.

## Requirements

### Functional Requirements

1. **Artifact Storage**
   - Store artifacts in S3 (organization-scoped)
   - Support multiple artifact types (CFN, Terraform, Lambda, diagrams, pricing, README)
   - Track artifact metadata in database

2. **Artifact Download**
   - Download individual artifacts
   - Download complete bundle (ZIP)
   - Pre-signed URLs for direct access

3. **Artifact Organization**
   - Link artifacts to sessions
   - Link artifacts to conversations
   - Organize by type and date

4. **Security**
   - User-scoped access control
   - Organization-scoped storage paths
   - Verify ownership before download

## S3 Storage Structure

```
s3://artifacts-bucket/
  organizations/
    {organization_id}/
      sessions/
        {session_id}/
          artifacts/
            cloudformation/
              main.yaml
              parameters.json
            terraform/
              main.tf
              variables.tf
              outputs.tf
              modules/
                vpc/
                  main.tf
            lambda/
              handler.py
              requirements.txt
            diagrams/
              architecture.png
              deployment.svg
            pricing/
              summary.pdf
              estimate.csv
            README.md
            bundle.zip (generated on-demand)
```

## Database Schema

### Artifacts Table

```sql
CREATE TABLE artifacts (
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(conversation_id) ON DELETE SET NULL,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL, -- 'cloudformation', 'terraform', 'lambda', 'diagram', 'pricing', 'readme'
    artifact_name VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL, -- Full S3 path
    file_size BIGINT NOT NULL, -- Bytes
    mime_type VARCHAR(100),
    metadata JSONB, -- Additional metadata (generation step, tool versions, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artifacts_session_id ON artifacts(session_id);
CREATE INDEX idx_artifacts_conversation_id ON artifacts(conversation_id);
CREATE INDEX idx_artifacts_org_id ON artifacts(organization_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
```

## API Specification

### GET /api/artifacts/list/{session_id}

**Response:**
```json
{
  "artifacts": [
    {
      "artifact_id": "uuid",
      "type": "cloudformation",
      "name": "main.yaml",
      "size": 15234,
      "mime_type": "application/x-yaml",
      "download_url": "/api/artifacts/download/{session_id}/cloudformation/main.yaml",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_size": 245678,
  "session_id": "uuid"
}
```

### GET /api/artifacts/download/{session_id}/{artifact_path}

**Response:**
File download with appropriate content-type headers

**Example:**
```
GET /api/artifacts/download/session123/cloudformation/main.yaml
→ Downloads main.yaml file
```

### GET /api/artifacts/bundle/{session_id}

**Response:**
ZIP file containing all artifacts for the session

**ZIP Structure:**
```
artifacts-bundle.zip
├── cloudformation/
│   └── main.yaml
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── lambda/
│   ├── handler.py
│   └── requirements.txt
├── diagrams/
│   └── architecture.png
├── pricing/
│   └── summary.pdf
└── README.md
```

### GET /api/artifacts/download-url/{session_id}/{artifact_path}

**Query Parameters:**
- `expires_in`: Seconds until expiration (default: 3600)

**Response:**
```json
{
  "download_url": "https://s3.amazonaws.com/...",
  "expires_at": "2024-01-15T11:30:00Z",
  "expires_in": 3600
}
```

## Backend Implementation

### Save Artifact to S3

```python
# backend/services/artifact_service.py
import boto3
from pathlib import Path

s3_client = boto3.client('s3')
ARTIFACTS_BUCKET = os.getenv("ARTIFACTS_BUCKET")

async def save_artifact(
    session_id: str,
    organization_id: str,
    artifact_type: str,
    artifact_name: str,
    content: bytes,
    metadata: dict = None
) -> str:
    """Save artifact to S3 and database"""
    
    # Generate S3 path
    s3_path = f"organizations/{organization_id}/sessions/{session_id}/artifacts/{artifact_type}/{artifact_name}"
    
    # Upload to S3
    s3_client.put_object(
        Bucket=ARTIFACTS_BUCKET,
        Key=s3_path,
        Body=content,
        ContentType=get_content_type(artifact_name),
        Metadata=metadata or {}
    )
    
    # Save metadata to database
    artifact = db.artifacts.create({
        "session_id": session_id,
        "organization_id": organization_id,
        "artifact_type": artifact_type,
        "artifact_name": artifact_name,
        "storage_path": s3_path,
        "file_size": len(content),
        "mime_type": get_content_type(artifact_name),
        "metadata": metadata
    })
    
    return artifact.artifact_id

def get_content_type(filename: str) -> str:
    """Determine content type from filename"""
    ext = Path(filename).suffix.lower()
    content_types = {
        '.yaml': 'application/x-yaml',
        '.yml': 'application/x-yaml',
        '.json': 'application/json',
        '.tf': 'text/plain',
        '.py': 'text/x-python',
        '.js': 'text/javascript',
        '.png': 'image/png',
        '.svg': 'image/svg+xml',
        '.pdf': 'application/pdf',
        '.md': 'text/markdown',
        '.csv': 'text/csv'
    }
    return content_types.get(ext, 'application/octet-stream')
```

### Download Artifact

```python
@router.get("/download/{session_id}/{artifact_path:path}")
async def download_artifact(
    session_id: str,
    artifact_path: str,
    user: dict = Depends(get_current_user)
):
    """Download individual artifact"""
    
    # Verify session ownership
    session = db.sessions.get(session_id)
    if not session or session.organization_id != user["org_id"]:
        raise HTTPException(404, "Session not found")
    
    # Construct S3 key
    s3_key = f"organizations/{user['org_id']}/sessions/{session_id}/artifacts/{artifact_path}"
    
    try:
        # Get object from S3
        obj = s3_client.get_object(Bucket=ARTIFACTS_BUCKET, Key=s3_key)
        content = obj['Body'].read()
        
        # Get content type
        content_type = obj.get('ContentType', 'application/octet-stream')
        
        # Determine filename
        filename = Path(artifact_path).name
        
        return Response(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except s3_client.exceptions.NoSuchKey:
        raise HTTPException(404, "Artifact not found")
```

### Generate Bundle ZIP

```python
@router.get("/bundle/{session_id}")
async def download_bundle(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """Download all artifacts as ZIP bundle"""
    
    # Verify ownership
    session = db.sessions.get(session_id)
    if not session or session.organization_id != user["org_id"]:
        raise HTTPException(404, "Session not found")
    
    # Get all artifacts for session
    artifacts = db.artifacts.get_by_session(session_id)
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for artifact in artifacts:
            # Download from S3
            obj = s3_client.get_object(
                Bucket=ARTIFACTS_BUCKET,
                Key=artifact.storage_path
            )
            
            # Add to ZIP with relative path
            relative_path = f"{artifact.artifact_type}/{artifact.artifact_name}"
            zip_file.writestr(relative_path, obj['Body'].read())
    
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="artifacts-{session_id}.zip"'
        }
    )
```

## Frontend Components

### Artifact Download Panel

```typescript
// frontend/components/artifacts/ArtifactDownload.tsx
export const ArtifactDownload: React.FC<{
  sessionId: string
}> = ({ sessionId }) => {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchArtifacts();
  }, [sessionId]);

  const fetchArtifacts = async () => {
    const response = await fetch(`/api/artifacts/list/${sessionId}`, {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    
    const data = await response.json();
    setArtifacts(data.artifacts);
    setIsLoading(false);
  };

  const downloadArtifact = async (artifact: Artifact) => {
    const url = `/api/artifacts/download/${sessionId}/${artifact.type}/${artifact.name}`;
    window.open(url, '_blank');
  };

  const downloadBundle = async () => {
    const url = `/api/artifacts/bundle/${sessionId}`;
    window.open(url, '_blank');
  };

  return (
    <div className="p-6 border rounded-lg space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Generated Artifacts</h3>
        <button
          onClick={downloadBundle}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Download All (ZIP)
        </button>
      </div>

      {isLoading ? (
        <div>Loading artifacts...</div>
      ) : artifacts.length === 0 ? (
        <div className="text-gray-500">No artifacts generated yet.</div>
      ) : (
        <div className="space-y-2">
          {artifacts.map(artifact => (
            <ArtifactItem
              key={artifact.artifact_id}
              artifact={artifact}
              onDownload={() => downloadArtifact(artifact)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

## Implementation Checklist

- [ ] Set up S3 bucket structure
- [ ] Implement artifact saving to S3
- [ ] Build artifact metadata storage
- [ ] Implement individual download endpoint
- [ ] Build bundle ZIP generation
- [ ] Add pre-signed URL support
- [ ] Implement access control
- [ ] Build frontend download UI
- [ ] Add artifact organization
- [ ] Write comprehensive tests

---

**Next Steps**: Proceed to Admin Portal design doc.

