"""
AWS Bedrock AI Engine Adapter
Implements converSQL adapter interface for Amazon Bedrock.
"""

import json
import os
from typing import Any, Dict, Optional, Tuple

from .base import AIEngineAdapter


class BedrockAdapter(AIEngineAdapter):
    """
    Amazon Bedrock AI engine adapter.

    Supports Claude models through AWS Bedrock infrastructure.
    Requires AWS credentials and appropriate IAM permissions.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Bedrock adapter.

        Args:
            config: Configuration dict with keys:
                - model_id: Bedrock model ID (default from env)
                - region: AWS region (default from env)
                - enable: Whether Bedrock is enabled (default True)
                - guardrail_id: Optional Bedrock Guardrail ID
                - guardrail_version: Optional Bedrock Guardrail version
        """
        self.client: Optional[Any] = None
        self.model_id: Optional[str] = None
        self.region: Optional[str] = None
        self.guardrail_id: Optional[str] = None
        self.guardrail_version: Optional[str] = None
        super().__init__(config)

    def _initialize(self) -> None:
        """Initialize Bedrock client with AWS SDK."""
        # Check if Bedrock is enabled
        enable_bedrock = self.config.get("enable", True)
        if not enable_bedrock:
            return

        # Get configuration
        self.model_id = self.config.get(
            "model_id", os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-haiku-20241022-v1:0")
        )
        self.region = self.config.get("region", os.getenv("AWS_DEFAULT_REGION", "us-west-2"))
        self.guardrail_id = self.config.get("guardrail_id", os.getenv("BEDROCK_GUARDRAIL_ID"))
        self.guardrail_version = self.config.get("guardrail_version", os.getenv("BEDROCK_GUARDRAIL_VERSION", "DRAFT"))

        try:
            import boto3
            from botocore.exceptions import NoCredentialsError, PartialCredentialsError

            # Check if AWS credentials are available
            try:
                session = boto3.Session()
                credentials = session.get_credentials()
                if credentials is None:
                    print("⚠️ No AWS credentials found for Bedrock")
                    print("   Configure credentials via AWS CLI, environment variables, or IAM role")
                    self.client = None
                    return

                # Verify credentials are actually usable (not just present but frozen/expired)
                frozen_creds = credentials.get_frozen_credentials()
                if not frozen_creds.access_key:
                    print("⚠️ AWS credentials are invalid or expired")
                    self.client = None
                    return

            except (NoCredentialsError, PartialCredentialsError) as e:
                print(f"⚠️ AWS credentials error: {e}")
                self.client = None
                return
            except Exception as e:
                print(f"⚠️ Error checking AWS credentials: {e}")
                self.client = None
                return

            # Initialize Bedrock runtime client
            self.client = boto3.client("bedrock-runtime", region_name=self.region)

            # Test credentials with a simple API call to verify they actually work
            try:
                # Try to list models - this will fail fast if credentials are invalid
                # We use the bedrock (not runtime) client for this test
                bedrock_client = boto3.client("bedrock", region_name=self.region)
                # Just call the API - if credentials are bad, this will raise an exception
                bedrock_client.list_foundation_models(maxResults=1)
                print(f"✅ AWS Bedrock initialized successfully in {self.region}")
            except Exception as e:
                # Credentials exist but are invalid (expired, wrong permissions, etc)
                print(f"⚠️ AWS Bedrock credentials are invalid: {e}")
                print("   Your AWS credentials exist but cannot access Bedrock services")
                self.client = None
                return

        except ImportError:
            print("⚠️ boto3 not installed. Run: pip install boto3")
            self.client = None
        except Exception as e:
            print(f"⚠️ Bedrock initialization failed: {e}")
            print("   Check AWS credentials and region configuration")
            self.client = None

    def is_available(self) -> bool:
        """Check if Bedrock client is initialized and ready."""
        return self.client is not None and self.model_id is not None

    def _generate_sql_impl(self, prompt: str) -> Tuple[str, str]:
        """
        Generate SQL using Amazon Bedrock.

        Args:
            prompt: Complete prompt with schema and question

        Returns:
            Tuple[str, str]: (sql_query, error_message)
        """
        if not self.is_available():
            return "", "Bedrock client not available. Check AWS credentials and configuration."

        try:
            # Build Bedrock request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.0,  # Deterministic for SQL generation
                "messages": [{"role": "user", "content": prompt}],
            }

            # Prepare invoke_model parameters
            model_id = self.model_id
            if model_id is None:
                return "", "Bedrock client not available. Check AWS configuration."

            invoke_params = {
                "modelId": model_id,
                "body": json.dumps(request_body),
                "contentType": "application/json",
                "accept": "application/json",
            }

            # Add guardrails if configured
            guardrail_id = self.guardrail_id
            guardrail_version = self.guardrail_version
            if guardrail_id is not None:
                invoke_params["guardrailIdentifier"] = guardrail_id
                if guardrail_version is not None:
                    invoke_params["guardrailVersion"] = guardrail_version

            # Call Bedrock API
            client = self.client
            if client is None:
                return "", "Bedrock client not available. Check AWS credentials and configuration."

            response = client.invoke_model(**invoke_params)

            # Parse response
            response_body = json.loads(response["body"].read())

            # Extract SQL from response
            if "content" in response_body and len(response_body["content"]) > 0:
                raw_sql = response_body["content"][0]["text"]
                sql_query = self.clean_sql_response(raw_sql)

                # Validate response
                is_valid, validation_msg = self.validate_response(sql_query)
                if not is_valid:
                    return "", f"Invalid SQL generated: {validation_msg}"

                return sql_query, ""
            else:
                return "", "Bedrock returned empty response"

        except Exception as e:
            error_msg = f"Bedrock API error: {str(e)}"

            # Provide helpful error messages for common issues
            error_lower = str(e).lower()
            if "credentials" in error_lower or "access denied" in error_lower:
                error_msg += "\nCheck AWS credentials (aws configure) or IAM permissions"
            elif "throttling" in error_lower or "rate" in error_lower:
                error_msg += "\nAPI rate limit exceeded. Try again in a moment"
            elif "model" in error_lower:
                error_msg += f"\nModel {self.model_id} may not be available in {self.region}"

            return "", error_msg

    @property
    def name(self) -> str:
        """Display name for this engine."""
        return "Amazon Bedrock"

    @property
    def provider_id(self) -> str:
        """Unique provider identifier."""
        return "bedrock"

    def get_model_info(self) -> Dict[str, Any]:
        """Get Bedrock model configuration details."""
        info: Dict[str, Any] = {
            "provider": "Amazon Bedrock",
            "model_id": self.model_id,
            "region": self.region,
            "service": "bedrock-runtime",
            "max_tokens": 4000,
            "temperature": 0.0,
            "capabilities": ["SQL generation", "Natural language understanding", "Schema comprehension"],
        }

        # Add guardrail info if configured
        if self.guardrail_id:
            info["guardrail_id"] = self.guardrail_id
            info["guardrail_version"] = self.guardrail_version
            info["capabilities"].append("Content filtering with Bedrock Guardrails")

        return info
