#!/bin/bash

# PostgreSQL AAD Principal Setup Script
# This script configures Azure AD authentication for the PostgreSQL Flexible Server
# and grants the necessary permissions to the managed identity

set -e

# Configuration variables
RESOURCE_GROUP="your-resource-group"
POSTGRES_SERVER_NAME="str-pg"
MANAGED_IDENTITY_NAME="str-backend-uami"
DATABASE_NAME="appdb"

echo "🔧 Setting up PostgreSQL AAD authentication..."

# Get the managed identity details
echo "📋 Getting managed identity information..."
MI_OBJECT_ID=$(az identity show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$MANAGED_IDENTITY_NAME" \
    --query principalId \
    --output tsv)

MI_CLIENT_ID=$(az identity show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$MANAGED_IDENTITY_NAME" \
    --query clientId \
    --output tsv)

echo "✅ Managed Identity Object ID: $MI_OBJECT_ID"
echo "✅ Managed Identity Client ID: $MI_CLIENT_ID"

# Get current user for AAD admin setup
CURRENT_USER_OBJECT_ID=$(az ad signed-in-user show --query id --output tsv)
CURRENT_USER_UPN=$(az ad signed-in-user show --query userPrincipalName --output tsv)

echo "📋 Current user: $CURRENT_USER_UPN ($CURRENT_USER_OBJECT_ID)"

# Set current user as AAD administrator (required for creating AAD principals)
echo "🔐 Setting AAD administrator..."
az postgres flexible-server ad-admin create \
    --resource-group "$RESOURCE_GROUP" \
    --server-name "$POSTGRES_SERVER_NAME" \
    --object-id "$CURRENT_USER_OBJECT_ID" \
    --principal-name "$CURRENT_USER_UPN" \
    --principal-type User

echo "✅ AAD administrator configured"

# Wait for the AAD admin to be fully configured
echo "⏳ Waiting for AAD configuration to propagate..."
sleep 30

# Get PostgreSQL connection string for AAD authentication
POSTGRES_HOST=$(az postgres flexible-server show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$POSTGRES_SERVER_NAME" \
    --query fullyQualifiedDomainName \
    --output tsv)

echo "🔗 PostgreSQL host: $POSTGRES_HOST"

# Create SQL script for setting up the managed identity
cat > setup_aad_user.sql << EOF
-- Create AAD user for the managed identity
-- Note: Use the managed identity name, not the object ID
SELECT 'CREATE USER IF NOT EXISTS "${MANAGED_IDENTITY_NAME}" WITH LOGIN;' as create_user;

-- Grant necessary permissions
GRANT CONNECT ON DATABASE ${DATABASE_NAME} TO "${MANAGED_IDENTITY_NAME}";
GRANT USAGE ON SCHEMA public TO "${MANAGED_IDENTITY_NAME}";
GRANT CREATE ON SCHEMA public TO "${MANAGED_IDENTITY_NAME}";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "${MANAGED_IDENTITY_NAME}";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "${MANAGED_IDENTITY_NAME}";

-- Grant permissions on future tables (for migrations)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "${MANAGED_IDENTITY_NAME}";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "${MANAGED_IDENTITY_NAME}";

-- Verify the user was created
SELECT rolname FROM pg_roles WHERE rolname = '${MANAGED_IDENTITY_NAME}';
EOF

echo "📝 SQL script created: setup_aad_user.sql"
echo ""
echo "🚨 MANUAL STEP REQUIRED:"
echo "Please run the following command to execute the SQL script:"
echo ""
echo "psql \"host=$POSTGRES_HOST port=5432 dbname=$DATABASE_NAME user=$CURRENT_USER_UPN sslmode=require\" -f setup_aad_user.sql"
echo ""
echo "You may need to install psql client first:"
echo "  - Ubuntu/Debian: sudo apt-get install postgresql-client"
echo "  - macOS: brew install postgresql"
echo "  - Windows: Download from PostgreSQL official site"
echo ""
echo "Alternative: Use Azure Data Studio or pgAdmin with AAD authentication"
echo ""
echo "📋 Connection details for manual setup:"
echo "  Host: $POSTGRES_HOST"
echo "  Port: 5432"
echo "  Database: $DATABASE_NAME"
echo "  User: $CURRENT_USER_UPN"
echo "  SSL Mode: require"
echo "  Authentication: Azure Active Directory"
echo ""
echo "🔧 After setting up the database user, test the connection with:"
echo "AZURE_CLIENT_ID=$MI_CLIENT_ID python test_db_connection.py"

# Create a test script for verifying the connection
cat > test_db_connection.py << 'EOF'
#!/usr/bin/env python3
"""Test script to verify PostgreSQL connection with managed identity."""

import os
import sys
import asyncio
from azure.identity import DefaultAzureCredential
import psycopg2

async def test_connection():
    """Test PostgreSQL connection using managed identity."""
    
    # Configuration from environment
    host = os.getenv('DATABASE_HOST', 'str-pg.postgres.database.azure.com')
    database = os.getenv('DATABASE_NAME', 'appdb')
    
    print(f"🔗 Testing connection to {host}/{database}")
    
    try:
        # Get Azure AD token
        credential = DefaultAzureCredential()
        token = credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
        
        print("✅ Successfully obtained Azure AD token")
        
        # Connect to PostgreSQL using the token as password
        connection = psycopg2.connect(
            host=host,
            port=5432,
            database=database,
            user=os.getenv('AZURE_CLIENT_ID'),  # Use client ID as username
            password=token.token,
            sslmode='require'
        )
        
        print("✅ Successfully connected to PostgreSQL")
        
        # Test basic query
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"📋 PostgreSQL version: {version[0]}")
        
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()
        print(f"👤 Connected as user: {user[0]}")
        
        # Test table creation (for migration permissions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("INSERT INTO test_connection DEFAULT VALUES;")
        connection.commit()
        
        cursor.execute("SELECT COUNT(*) FROM test_connection;")
        count = cursor.fetchone()
        print(f"✅ Test table operations successful, rows: {count[0]}")
        
        # Cleanup
        cursor.execute("DROP TABLE test_connection;")
        connection.commit()
        
        cursor.close()
        connection.close()
        
        print("🎉 All tests passed! Managed identity authentication is working correctly.")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("💡 Make sure:")
        print("  1. You've run the SQL setup script")
        print("  2. The managed identity has been granted database permissions")
        print("  3. AZURE_CLIENT_ID environment variable is set")
        print("  4. The application is running with the managed identity")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())
EOF

chmod +x test_db_connection.py

echo "✅ Test script created: test_db_connection.py"
echo ""
echo "📋 Next steps:"
echo "1. Run the SQL script manually (see command above)"
echo "2. Test the connection: AZURE_CLIENT_ID=$MI_CLIENT_ID python test_db_connection.py"
echo "3. Update your application environment variables:"
echo "   - DATABASE_HOST=$POSTGRES_HOST"
echo "   - DATABASE_NAME=$DATABASE_NAME"
echo "   - AZURE_CLIENT_ID=$MI_CLIENT_ID"
echo "4. Deploy your application with the managed identity"
echo ""
echo "🔐 Security notes:"
echo "- Password authentication is disabled on this PostgreSQL server"
echo "- Only Azure AD authentication is allowed"
echo "- Database is only accessible via private network (VNet)"
echo "- No public internet access to the database"