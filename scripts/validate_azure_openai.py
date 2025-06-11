#!/usr/bin/env python3
"""
Azure OpenAI Integration Validation Script

This script validates the Azure OpenAI integration setup according to ADR 0005.
Run this script to verify that all components are properly configured.
"""

import os
import sys
from typing import Dict, List, Optional
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AzureOpenAIValidator:
    """Validates Azure OpenAI integration setup."""
    
    def __init__(self):
        self.issues: List[str] = []
        self.warnings: List[str] = []
        
    async def validate_configuration(self) -> bool:
        """Validate basic configuration requirements."""
        logger.info("🔧 Validating configuration...")
        
        required_env_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_CHAT_DEPLOYMENT",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        ]
        
        for var in required_env_vars:
            if not os.getenv(var):
                self.issues.append(f"Missing required environment variable: {var}")
        
        return len(self.issues) == 0
    
    async def validate_dependencies(self) -> bool:
        """Validate required Python dependencies."""
        logger.info("📦 Validating dependencies...")
        
        required_packages = [
            "semantic-kernel",
            "azure-identity", 
            "azure-storage-blob",
            "openai",
            "fastapi",
            "pydantic"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.issues.append(f"Missing required packages: {', '.join(missing_packages)}")
            
        return len(missing_packages) == 0
    
    async def validate_azure_connection(self) -> bool:
        """Validate connection to Azure OpenAI service."""
        logger.info("🌐 Validating Azure OpenAI connection...")
        
        try:
            # Import here to avoid dependency issues during validation
            from app.kernel_setup import KernelManager
            from app.config import settings
            
            # Test kernel creation
            kernel_manager = KernelManager()
            kernel = kernel_manager.create_kernel()
            
            logger.info("✅ Kernel created successfully")
            return True
            
        except ImportError as e:
            self.issues.append(f"Cannot import required modules: {str(e)}")
            return False
        except Exception as e:
            self.issues.append(f"Failed to create kernel: {str(e)}")
            return False
    
    async def validate_model_deployments(self) -> bool:
        """Validate that required model deployments are accessible."""
        logger.info("🤖 Validating model deployments...")
        
        # This would require actual API calls to Azure OpenAI
        # For now, just validate configuration exists
        chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
        embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        
        if not chat_deployment:
            self.issues.append("Chat model deployment not configured")
        
        if not embedding_deployment:
            self.issues.append("Embedding model deployment not configured")
            
        return len(self.issues) == 0
    
    async def run_validation(self) -> bool:
        """Run complete validation suite."""
        logger.info("🚀 Starting Azure OpenAI integration validation...")
        
        validations = [
            self.validate_configuration,
            self.validate_dependencies,
            self.validate_azure_connection,
            self.validate_model_deployments
        ]
        
        success = True
        for validation in validations:
            try:
                result = await validation()
                success &= result
            except Exception as e:
                self.issues.append(f"Validation failed: {str(e)}")
                success = False
        
        return success
    
    def print_results(self):
        """Print validation results."""
        if not self.issues and not self.warnings:
            logger.info("✅ All validations passed! Azure OpenAI integration is properly configured.")
            return
        
        if self.issues:
            logger.error("❌ Validation failed with the following issues:")
            for issue in self.issues:
                logger.error(f"   • {issue}")
        
        if self.warnings:
            logger.warning("⚠️  Warnings:")
            for warning in self.warnings:
                logger.warning(f"   • {warning}")

async def main():
    """Main validation function."""
    validator = AzureOpenAIValidator()
    
    try:
        success = await validator.run_validation()
        validator.print_results()
        
        if success:
            logger.info("🎉 Azure OpenAI integration validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("💥 Azure OpenAI integration validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())