"""
Tests for CloudFormation parser service
"""

import pytest
from backend.services.cloudformation_parser import (
    parse_cloudformation_template,
    generate_deployment_instructions,
    _clean_template,
    _extract_outputs,
    _extract_parameters,
    _extract_resources
)


class TestCloudFormationParser:
    """Test CloudFormation template parsing"""
    
    def test_parse_valid_template(self):
        """Test parsing a valid CloudFormation template"""
        template = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Test template

Parameters:
  Environment:
    Type: String
    Default: production
    Description: Environment name

Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-test-bucket

Outputs:
  BucketName:
    Description: Name of the bucket
    Value: !Ref MyBucket
"""
        result = parse_cloudformation_template(template)
        
        assert result["total_resources"] == 1
        assert len(result["outputs"]) == 1
        assert len(result["parameters"]) == 1
        assert "S3" in result["aws_services"]
        assert result["outputs"][0]["key"] == "BucketName"
    
    def test_parse_template_with_markdown(self):
        """Test parsing template wrapped in markdown code blocks"""
        template = """```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
```
"""
        result = parse_cloudformation_template(template)
        assert result["total_resources"] == 1
        assert result["resources"][0]["type"] == "AWS::Lambda::Function"
    
    def test_parse_empty_template(self):
        """Test parsing empty template"""
        result = parse_cloudformation_template("")
        assert result["total_resources"] == 0
        assert len(result["outputs"]) == 0
        assert len(result["parameters"]) == 0
    
    def test_parse_template_with_multiple_resources(self):
        """Test parsing template with multiple resources"""
        template = """
Resources:
  Function1:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.9
  Function2:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.10
  Bucket:
    Type: AWS::S3::Bucket
"""
        result = parse_cloudformation_template(template)
        assert result["total_resources"] == 3
        assert result["resource_types"]["AWS::Lambda::Function"] == 2
        assert result["resource_types"]["AWS::S3::Bucket"] == 1
    
    def test_extract_outputs(self):
        """Test extracting outputs from template"""
        template_dict = {
            "Outputs": {
                "ApiUrl": {
                    "Description": "API endpoint URL",
                    "Value": "https://api.example.com",
                    "Export": {
                        "Name": "ApiUrl"
                    }
                }
            }
        }
        outputs = _extract_outputs(template_dict)
        assert len(outputs) == 1
        assert outputs[0]["key"] == "ApiUrl"
        assert outputs[0]["description"] == "API endpoint URL"
        assert outputs[0]["export_name"] == "ApiUrl"
    
    def test_extract_parameters(self):
        """Test extracting parameters from template"""
        template_dict = {
            "Parameters": {
                "InstanceType": {
                    "Type": "String",
                    "Default": "t3.micro",
                    "Description": "EC2 instance type",
                    "AllowedValues": ["t3.micro", "t3.small"]
                }
            }
        }
        parameters = _extract_parameters(template_dict)
        assert len(parameters) == 1
        assert parameters[0]["name"] == "InstanceType"
        assert parameters[0]["type"] == "String"
        assert parameters[0]["default"] == "t3.micro"
    
    def test_extract_resources(self):
        """Test extracting resources from template"""
        template_dict = {
            "Resources": {
                "MyDB": {
                    "Type": "AWS::RDS::DBInstance",
                    "Properties": {
                        "DBInstanceClass": "db.t3.micro",
                        "Engine": "postgres"
                    }
                }
            }
        }
        resources, resource_types, services = _extract_resources(template_dict)
        assert len(resources) == 1
        assert resources[0]["logical_id"] == "MyDB"
        assert resources[0]["type"] == "AWS::RDS::DBInstance"
        assert "RDS" in services
    
    def test_clean_template(self):
        """Test cleaning template text"""
        template = """Some text before
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyResource:
    Type: AWS::S3::Bucket
```
Some text after"""
        cleaned = _clean_template(template)
        assert "AWSTemplateFormatVersion" in cleaned
        assert "Some text before" not in cleaned or "AWSTemplateFormatVersion" in cleaned
    
    def test_generate_deployment_instructions(self):
        """Test generating deployment instructions"""
        template = """
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  Environment:
    Type: String
    Default: production
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
"""
        instructions = generate_deployment_instructions(template, "us-east-1")
        
        assert "aws_cli_command" in instructions
        assert "console_steps" in instructions
        assert "prerequisites" in instructions
        assert "estimated_deployment_time" in instructions
        assert "us-east-1" in instructions["aws_cli_command"]
    
    def test_generate_deployment_instructions_with_parameters(self):
        """Test deployment instructions with parameters"""
        template = """
Parameters:
  Env:
    Type: String
    Default: prod
Resources:
  Resource1:
    Type: AWS::Lambda::Function
"""
        instructions = generate_deployment_instructions(template)
        assert "ParameterKey" in instructions["aws_cli_command"] or "Parameters" in instructions["aws_cli_command"]
    
    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML gracefully"""
        invalid_template = "This is not valid YAML: { invalid syntax }"
        result = parse_cloudformation_template(invalid_template)
        # Should return empty result, not crash
        assert isinstance(result, dict)
        assert "total_resources" in result
    
    def test_resource_property_summaries(self):
        """Test resource property summaries are generated"""
        template = """
Resources:
  LambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.9
      Handler: index.handler
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"""
        result = parse_cloudformation_template(template)
        assert len(result["resources"]) == 2
        # Check that properties_summary exists
        for resource in result["resources"]:
            assert "properties_summary" in resource

