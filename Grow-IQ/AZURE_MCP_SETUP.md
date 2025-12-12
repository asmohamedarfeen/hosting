# Azure MCP Setup for Cursor

## ✅ Configuration Complete

Azure MCP Server has been successfully added to your Cursor configuration file at `~/.cursor/mcp.json`.

## 📋 Next Steps

### 1. Install Azure CLI (if not already installed)

```bash
brew install azure-cli
```

### 2. Login to Azure

After installing Azure CLI, authenticate to your Azure account:

```bash
az login
```

This will open a browser window for authentication.

### 3. Verify Authentication

Check that you're authenticated:

```bash
az account show
```

This should display your Azure subscription details.

### 4. Restart Cursor

**IMPORTANT:** You must restart Cursor for the MCP configuration changes to take effect.

1. Close Cursor completely
2. Reopen Cursor
3. The Azure MCP Server should now be available

### 5. Test Azure MCP Integration

Once Cursor restarts, you can test the Azure MCP by:

1. Open Cursor's AI chat (Ctrl+L or Cmd+L)
2. Try prompts like:
   - "List my Azure storage accounts"
   - "Show me my Azure App Services"
   - "List my Azure resource groups"
   - "Create an Azure App Service for my application"

### 6. Required Permissions

Make sure your Azure account has the necessary permissions:
- **Contributor** or **Owner** role on your subscription for resource management
- **Reader** role at minimum for viewing resources

You can check your roles with:
```bash
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

## 🔧 Configuration Details

The Azure MCP Server is configured in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "Azure MCP Server": {
      "command": "npx",
      "args": [
        "-y",
        "@azure/mcp@latest",
        "server",
        "start"
      ]
    }
  }
}
```

## 📚 Available Azure MCP Commands

Once connected, you can use Azure MCP to:

- **Resource Management**: Create, list, update, and delete Azure resources
- **App Service Operations**: Deploy and manage web applications
- **Database Management**: Manage Azure SQL, PostgreSQL, and other databases
- **Storage Operations**: Manage Azure Blob Storage, File Storage
- **Monitoring**: View metrics, logs, and diagnostics
- **Configuration**: Manage App Service settings, connection strings, etc.

## 🔍 Troubleshooting

### MCP Server not appearing in Cursor

1. Verify `~/.cursor/mcp.json` has the correct configuration
2. Restart Cursor completely (quit and reopen)
3. Check Cursor's MCP settings: `File > Preferences > Cursor Settings > Tools & Integrations`

### Authentication Issues

1. Run `az login` again
2. Verify with `az account show`
3. Check you have the correct Azure subscription selected:
   ```bash
   az account list --output table
   az account set --subscription "Your Subscription Name"
   ```

### Permission Errors

If you get permission errors:
1. Verify your Azure role assignments
2. Contact your Azure administrator to grant necessary permissions
3. Ensure you're using the correct Azure subscription

## 🎯 Use Cases for Your Application

With Azure MCP connected, you can:

1. **Deploy your application directly from Cursor**:
   - "Create an Azure App Service for my FastAPI application"
   - "Set up Azure PostgreSQL database for my app"
   - "Configure environment variables for my Azure App Service"

2. **Manage Azure resources**:
   - "List all my Azure App Services"
   - "Show the status of my Azure databases"
   - "Get the connection string for my PostgreSQL database"

3. **Monitor and troubleshoot**:
   - "Show logs from my Azure App Service"
   - "Check the health of my Azure resources"
   - "View metrics for my application"

4. **Deploy configurations**:
   - "Update my App Service with the new environment variables"
   - "Configure CORS settings for my Azure App Service"
   - "Set up SSL certificates for my domain"

## 🔐 Security Notes

- Azure CLI credentials are stored locally in `~/.azure/`
- MCP Server uses your existing Azure CLI authentication
- No additional API keys are required
- Always use secure practices when managing Azure resources

## 📞 Support

If you encounter issues:
1. Check [Azure MCP Documentation](https://learn.microsoft.com/en-us/azure/developer/azure-mcp-server/)
2. Verify Azure CLI is working: `az --version`
3. Check Cursor MCP logs (if available in Cursor settings)

