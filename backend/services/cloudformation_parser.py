"""
CloudFormation Template Parser
Extracts outputs, parameters, resources, and generates deployment instructions
"""

import yaml
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


def parse_cloudformation_template(template_content: str) -> Dict[str, Any]:
    """
    Parse CloudFormation template and extract structured information
    
    Returns:
        {
            "outputs": List of output definitions,
            "parameters": List of parameter definitions,
            "resources": List of resource summaries,
            "resource_types": Dict of resource type counts,
            "total_resources": int,
            "aws_services": List of AWS services used
        }
    """
    try:
        # Clean template - remove markdown code blocks if present
        clean_template = _clean_template(template_content)
        
        # Parse YAML
        try:
            template_dict = yaml.safe_load(clean_template)
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML: {e}")
            # Try to extract YAML from markdown or other formats
            clean_template = _extract_yaml_from_text(clean_template)
            template_dict = yaml.safe_load(clean_template)
        
        if not template_dict:
            return _empty_result()
        
        # Extract outputs
        outputs = _extract_outputs(template_dict)
        
        # Extract parameters
        parameters = _extract_parameters(template_dict)
        
        # Extract resources
        resources, resource_types, aws_services = _extract_resources(template_dict)
        
        return {
            "outputs": outputs,
            "parameters": parameters,
            "resources": resources,
            "resource_types": resource_types,
            "total_resources": len(resources),
            "aws_services": aws_services
        }
    
    except Exception as e:
        logger.error(f"Error parsing CloudFormation template: {e}")
        return _empty_result()


def _clean_template(template: str) -> str:
    """Remove markdown code blocks and extract YAML content"""
    # Remove markdown code blocks
    template = re.sub(r'```(?:yaml|yml)?\s*\n?', '', template)
    template = re.sub(r'```\s*$', '', template)
    
    # Find YAML start (AWSTemplateFormatVersion, Resources, Parameters, etc.)
    yaml_start_patterns = [
        r'AWSTemplateFormatVersion',
        r'^Resources:',
        r'^Parameters:',
        r'^Outputs:',
        r'^Mappings:',
        r'^Conditions:',
        r'^Transform:',
        r'^---',
    ]
    
    for pattern in yaml_start_patterns:
        match = re.search(pattern, template, re.MULTILINE)
        if match:
            return template[match.start():].strip()
    
    return template.strip()


def _extract_yaml_from_text(text: str) -> str:
    """Extract YAML content from text that might contain other content"""
    # Look for YAML-like structure
    yaml_match = re.search(
        r'(AWSTemplateFormatVersion|Resources:|Parameters:|Outputs:)[\s\S]*',
        text,
        re.MULTILINE
    )
    if yaml_match:
        return yaml_match.group(0)
    return text


def _extract_outputs(template_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract outputs from template"""
    outputs = []
    outputs_section = template_dict.get("Outputs", {})
    
    for output_name, output_def in outputs_section.items():
        outputs.append({
            "key": output_name,
            "description": output_def.get("Description", ""),
            "value": output_def.get("Value", ""),
            "export_name": output_def.get("Export", {}).get("Name", "") if isinstance(output_def.get("Export"), dict) else ""
        })
    
    return outputs


def _extract_parameters(template_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract parameters from template"""
    parameters = []
    parameters_section = template_dict.get("Parameters", {})
    
    for param_name, param_def in parameters_section.items():
        parameters.append({
            "name": param_name,
            "type": param_def.get("Type", "String"),
            "default": param_def.get("Default", ""),
            "description": param_def.get("Description", ""),
            "allowed_values": param_def.get("AllowedValues", []),
            "min_value": param_def.get("MinValue"),
            "max_value": param_def.get("MaxValue")
        })
    
    return parameters


def _extract_resources(template_dict: Dict[str, Any]) -> tuple[List[Dict[str, Any]], Dict[str, int], List[str]]:
    """Extract resources from template"""
    resources = []
    resource_types: Dict[str, int] = {}
    aws_services: List[str] = []
    
    resources_section = template_dict.get("Resources", {})
    
    for logical_id, resource_def in resources_section.items():
        resource_type = resource_def.get("Type", "")
        
        # Extract AWS service name from resource type (e.g., AWS::S3::Bucket -> S3)
        if resource_type.startswith("AWS::"):
            service_parts = resource_type.split("::")
            if len(service_parts) >= 2:
                service_name = service_parts[1]
                if service_name not in aws_services:
                    aws_services.append(service_name)
        
        # Count resource types
        resource_types[resource_type] = resource_types.get(resource_type, 0) + 1
        
        # Extract key properties
        properties = resource_def.get("Properties", {})
        properties_summary = _summarize_properties(properties, resource_type)
        
        resources.append({
            "logical_id": logical_id,
            "type": resource_type,
            "properties_summary": properties_summary
        })
    
    return resources, resource_types, aws_services


def _summarize_properties(properties: Dict[str, Any], resource_type: str) -> str:
    """Create a summary of resource properties"""
    if not properties:
        return "No properties specified"
    
    # Extract key properties based on resource type
    key_props = []
    
    if "AWS::S3::Bucket" in resource_type:
        key_props.append(f"BucketName: {properties.get('BucketName', 'auto-generated')}")
    elif "AWS::Lambda::Function" in resource_type:
        key_props.append(f"Runtime: {properties.get('Runtime', 'N/A')}")
        key_props.append(f"Handler: {properties.get('Handler', 'N/A')}")
    elif "AWS::EC2::Instance" in resource_type:
        key_props.append(f"InstanceType: {properties.get('InstanceType', 'N/A')}")
    elif "AWS::RDS::DBInstance" in resource_type:
        key_props.append(f"DBInstanceClass: {properties.get('DBInstanceClass', 'N/A')}")
        key_props.append(f"Engine: {properties.get('Engine', 'N/A')}")
    elif "AWS::DynamoDB::Table" in resource_type:
        key_props.append(f"TableName: {properties.get('TableName', 'N/A')}")
    
    # Add first few properties if no specific ones found
    if not key_props and properties:
        for key, value in list(properties.items())[:3]:
            if isinstance(value, (str, int, float, bool)):
                key_props.append(f"{key}: {value}")
    
    return ", ".join(key_props) if key_props else "Properties configured"


def generate_deployment_instructions(template_content: str, region: str = "us-east-1") -> Dict[str, Any]:
    """
    Generate deployment instructions for CloudFormation template
    
    Returns:
        {
            "aws_cli_command": str,
            "console_steps": List[str],
            "prerequisites": List[str],
            "estimated_deployment_time": str
        }
    """
    # Parse template to get stack name suggestion
    parsed = parse_cloudformation_template(template_content)
    
    # Generate AWS CLI command
    stack_name = "my-stack"  # Default, user should customize
    aws_cli_command = f"aws cloudformation create-stack \\\n  --stack-name {stack_name} \\\n  --template-body file://cloudformation-template.yaml \\\n  --region {region}"
    
    # Add parameters if any exist
    if parsed["parameters"]:
        params = []
        for param in parsed["parameters"][:5]:  # Limit to first 5
            if param.get("default"):
                params.append(f"{param['name']}={param['default']}")
        if params:
            aws_cli_command += f" \\\n  --parameters ParameterKey={params[0]}"
            for param in params[1:]:
                aws_cli_command += f" ParameterKey={param.split('=')[0]} ParameterValue={param.split('=')[1]}"
    
    # Console steps
    console_steps = [
        "1. Open AWS CloudFormation Console",
        "2. Click 'Create stack' → 'With new resources (standard)'",
        "3. Upload template file or paste template content",
        "4. Enter stack name and configure parameters",
        "5. Review and create stack"
    ]
    
    # Prerequisites
    prerequisites = [
        "AWS CLI configured with appropriate credentials",
        f"AWS account with permissions to create resources in {region}",
        "Template file saved locally (for CLI deployment)"
    ]
    
    # Estimate deployment time
    total_resources = parsed["total_resources"]
    if total_resources < 5:
        estimated_time = "1-3 minutes"
    elif total_resources < 20:
        estimated_time = "3-10 minutes"
    else:
        estimated_time = "10-30 minutes"
    
    return {
        "aws_cli_command": aws_cli_command,
        "console_steps": console_steps,
        "prerequisites": prerequisites,
        "estimated_deployment_time": estimated_time
    }


def _empty_result() -> Dict[str, Any]:
    """Return empty result structure"""
    return {
        "outputs": [],
        "parameters": [],
        "resources": [],
        "resource_types": {},
        "total_resources": 0,
        "aws_services": []
    }

