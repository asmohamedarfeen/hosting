# MCP Servers Available in Cursor

## 📊 Summary

**Total MCP Servers Installed & Enabled: 5**

**Browser Automation Status**: ✅ Ready (Chrome detected)

---

## 🔍 Detailed List of MCP Servers

### 1. **Framelink MCP for Figma** ✅ ENABLED
**Status**: Active | **Tools**: 2 enabled

**Purpose**: Figma design integration and asset management

**Available Functions**:
- `get_figma_data` - Get comprehensive Figma file data including layout, content, visuals, and component information
- `download_figma_images` - Download SVG and PNG images from Figma files

**Use Cases**:
- Extract design specifications from Figma
- Download design assets (icons, images, SVGs)
- Get component information for implementation

---

### 2. **Magic MCP (21st.dev Integration)** ✅ ENABLED
**Status**: Active | **Tools**: 4 enabled

**Purpose**: UI component generation and logo search

**Available Functions**:
- `magic_component_builder` - Generate new UI components (buttons, inputs, dialogs, tables, forms, etc.)
- `magic_component_inspiration` - Get component inspiration and previews from 21st.dev
- `magic_component_refiner` - Redesign/refine/improve existing UI components
- `logo_search` - Search and return company logos in JSX, TSX, or SVG format

**Use Cases**:
- Generate React components quickly
- Find UI component inspiration
- Improve existing components
- Add company logos to projects

---

### 3. **shadcn MCP** ✅ ENABLED
**Status**: Active | **Tools**: 7 enabled

**Purpose**: shadcn/ui component management

**Available Functions**:
- `get_project_registries` - Get configured registry names from components.json
- `list_items_in_registries` - List items from registries
- `search_items_in_registries` - Search for components using fuzzy matching
- `view_items_in_registries` - View detailed information about specific registry items
- `get_item_examples_from_registries` - Find usage examples and demos with complete code
- `get_add_command_for_items` - Get shadcn CLI add command for specific items
- `get_audit_checklist` - Quick checklist to verify components are working

**Use Cases**:
- Manage shadcn/ui components
- Search for existing components
- Get component examples
- Add new shadcn components to project

---

### 4. **Chrome DevTools MCP** ✅ ENABLED
**Status**: Active | **Tools**: 26 enabled

**Purpose**: Browser automation and debugging

**Available Functions** (26 tools):
- **Navigation**: `navigate_page`, `new_page`, `close_page`, `select_page`, `list_pages`
- **Interaction**: `click`, `fill`, `fill_form`, `press_key`, `hover`, `drag`, `upload_file`
- **Inspection**: `take_snapshot`, `take_screenshot`, `evaluate_script`
- **Network**: `list_network_requests`, `get_network_request`
- **Console**: `list_console_messages`, `get_console_message`
- **Performance**: `performance_start_trace`, `performance_stop_trace`, `performance_analyze_insight`
- **Emulation**: `emulate` (network conditions, CPU throttling)
- **Dialogs**: `handle_dialog`
- **Utilities**: `wait_for`, `resize_page`

**Use Cases**:
- Automated browser testing
- Web scraping
- Performance analysis
- Debugging web applications
- UI testing

---

### 5. **Playwright MCP** ✅ ENABLED
**Status**: Active | **Tools**: 22 enabled

**Purpose**: Playwright-based browser automation

**Available Functions** (22 tools):
- **Navigation**: `navigate`, `navigate_back`, `tabs` (list, create, close, select)
- **Interaction**: `click`, `type`, `fill_form`, `select_option`, `press_key`, `hover`, `drag`
- **Inspection**: `snapshot`, `take_screenshot`, `evaluate`
- **Network**: `network_requests`
- **Console**: `console_messages`
- **Dialogs**: `handle_dialog`
- **File Upload**: `file_upload`
- **Utilities**: `wait_for`, `resize`, `install`

**Use Cases**:
- End-to-end testing
- Browser automation
- Web application testing
- Screenshot generation
- Accessibility testing

---

### 6. **Azure MCP Server** (Documented but may require setup)
**Purpose**: Azure cloud resource management

**Documented Capabilities** (from AZURE_MCP_SETUP.md):
- Resource Management: Create, list, update, and delete Azure resources
- App Service Operations: Deploy and manage web applications
- Database Management: Manage Azure SQL, PostgreSQL, and other databases
- Storage Operations: Manage Azure Blob Storage, File Storage
- Monitoring: View metrics, logs, and diagnostics
- Configuration: Manage App Service settings, connection strings, etc.

**Setup Required**:
- Azure CLI installation
- Azure account authentication (`az login`)
- Configuration in `~/.cursor/mcp.json`

**Status**: ⚠️ Requires manual configuration (see AZURE_MCP_SETUP.md)

---

## 📈 MCP Server Usage Statistics

| MCP Server | Tools Enabled | Status | Primary Use Case |
|------------|---------------|--------|------------------|
| Chrome DevTools MCP | 26 | ✅ Enabled | Browser automation & testing |
| Playwright MCP | 22 | ✅ Enabled | E2E testing & automation |
| shadcn MCP | 7 | ✅ Enabled | Component management |
| Magic MCP | 4 | ✅ Enabled | UI component generation |
| Framelink MCP | 2 | ✅ Enabled | Figma integration |
| **TOTAL** | **61 tools** | **All Active** | **Full automation suite** |

---

## 🎯 Recommended Use Cases for Your Application

### For Testing & Quality Assurance:
- **Chrome DevTools MCP** or **cursor-playwright MCP**: Test all routes, authentication flows, UI components

### For UI Development:
- **Magic MCP**: Generate new components quickly
- **shadcn MCP**: Manage existing shadcn components
- **Framelink MCP**: Extract designs from Figma

### For Deployment:
- **Azure MCP**: Deploy to Azure App Service, manage databases, configure resources

---

## ⚙️ Configuration Status

### ✅ All MCP Servers Active & Ready:
1. ✅ **Framelink MCP for Figma** - 2 tools enabled
2. ✅ **Magic MCP (21st.dev)** - 4 tools enabled
3. ✅ **shadcn MCP** - 7 tools enabled
4. ✅ **Playwright MCP** - 22 tools enabled
5. ✅ **Chrome DevTools MCP** - 26 tools enabled

### 🌐 Browser Automation:
- ✅ **Chrome Detected**: Ready for browser automation
- ✅ **Total Automation Tools**: 48 tools (26 Chrome DevTools + 22 Playwright)

### ⚠️ Optional (Not Installed):
- Azure MCP Server (see AZURE_MCP_SETUP.md for setup instructions)

---

## 📝 Notes

- **MCP Resources**: Currently showing "No MCP resources found" - this is normal as resources are typically project-specific
- **LM Studio**: Documented but configured as a model provider, not an MCP server
- **Google OAuth**: Configured in the application but not as an MCP server

---

## 🚀 Next Steps

To use these MCP servers:
1. **For browser testing**: Use Chrome DevTools or cursor-playwright MCP to test your application
2. **For UI components**: Use Magic MCP or shadcn MCP to enhance your frontend
3. **For Azure deployment**: Follow AZURE_MCP_SETUP.md to configure Azure MCP
4. **For design assets**: Use Framelink MCP to extract Figma designs

---

**Last Updated**: 2025-11-21
**Total MCP Servers Installed**: 5 (All enabled and active)
**Total Tools Available**: 61 tools across all servers
**Browser Automation**: ✅ Ready (Chrome detected)

