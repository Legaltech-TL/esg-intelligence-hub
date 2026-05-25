# ESG Intelligence Hub - GitHub Actions Edition

**Fully automated ESG news aggregation with GitHub Actions (FREE) + Power Automate + SharePoint**

---

## 🎯 Why GitHub Actions > Azure Functions

| Feature | GitHub Actions | Azure Functions |
|---------|---------------|-----------------|
| **Cost** | **FREE** (2000 min/month) | ₹300-500/month |
| **Setup** | Git push | Azure Portal config |
| **Logs** | GitHub UI | Azure Portal |
| **Version Control** | Native | Manual |
| **Secrets** | GitHub Secrets | Azure Key Vault |
| **Testing** | Manual dispatch | Portal testing |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────┐
│  GitHub Actions (Runs daily 6 AM IST) │
│  1. Fetch keywords from SharePoint    │
│  2. Fetch sources from SharePoint     │
│  3. Scrape RSS feeds + websites        │
│  4. AI summarization (Claude)          │
│  5. POST to Power Automate webhook    │
└────────────────────────────────────────┘
                  ↓ (HTTP)
┌────────────────────────────────────────┐
│  Power Automate Flow                   │
│  1. Receives articles from GitHub      │
│  2. Stores in SharePoint Lists         │
│  3. Builds personalized email          │
│  4. Sends HTML digest to recipients    │
└────────────────────────────────────────┘
```

---

## 📦 What's Included

```
esg-hub-github/
├── .github/workflows/
│   └── daily-esg-scraper.yml      # Main workflow
├── scripts/
│   ├── fetch_keywords.py          # Get keywords from SharePoint
│   ├── fetch_sources.py           # Get sources from SharePoint
│   ├── scrape_all.py              # Main scraper (RSS + Web)
│   ├── summarize_articles.py     # Claude AI summarization
│   └── send_to_power_automate.py # POST to webhook
├── config/
│   ├── keywords.csv               # 180+ ESG keywords (fallback)
│   └── sources.csv                # 17 sources (fallback)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🚀 Setup (30 Minutes)

### Step 1: Fork/Create GitHub Repository

1. Create new private repository: `esg-intelligence-hub`
2. Upload all files from this folder
3. Go to **Settings** → **Secrets and variables** → **Actions**

### Step 2: Configure GitHub Secrets

Add these secrets:

**Required:**
- `ANTHROPIC_API_KEY` - Your Claude API key
- `POWER_AUTOMATE_WEBHOOK` - Power Automate HTTP trigger URL

**Optional (for SharePoint integration):**
- `SHAREPOINT_SITE` - e.g., `https://trilegal.sharepoint.com/sites/ESGHub`
- `SHAREPOINT_CLIENT_ID` - Azure AD App ID
- `SHAREPOINT_CLIENT_SECRET` - Azure AD App Secret

> **Note:** If SharePoint secrets not provided, system uses local CSV files as fallback

---

### Step 3: Create Power Automate Flow

**Flow Name:** `ESG_Receive_And_Store`

**Trigger:** HTTP - When a HTTP request is received

**Request Body Schema:**
```json
{
    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string"
        },
        "executive_summary": {
            "type": "string"
        },
        "total_articles": {
            "type": "integer"
        },
        "articles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "link": {"type": "string"},
                    "summary": {"type": "string"},
                    "ai_summary": {"type": "string"},
                    "category": {"type": "string"},
                    "relevance_score": {"type": "number"},
                    "source": {"type": "string"},
                    "matched_keywords": {"type": "array"},
                    "action_items": {"type": "array"}
                }
            }
        }
    }
}
```

**Flow Steps:**

1. **HTTP Trigger** (get webhook URL, add to GitHub Secrets)
2. **Apply to each** - Loop through `triggerBody()?['articles']`
3. **SharePoint - Create item** in `ESG_Articles`:
   - Title: `item()?['title']`
   - SourceURL: `item()?['link']`
   - AISummary: `item()?['ai_summary']`
   - ArticleCategory: `item()?['category']`
   - RelevanceScore: `item()?['relevance_score']`
   - MatchedKeywords: `string(item()?['matched_keywords'])`
   - ArticleStatus: `New`
   - ScrapedDate: `utcNow()`
4. **Compose Email** - Use email template
5. **Send email** - Office 365 Outlook

---

### Step 4: Test the Workflow

**Manual Trigger:**
1. Go to **Actions** tab in GitHub
2. Select "Daily ESG News Scraper"
3. Click **Run workflow** → **Run workflow**
4. Wait 5-10 minutes
5. Check **Actions** tab for logs
6. Check SharePoint for new articles
7. Check your email inbox

---

## 🔐 Setting Up SharePoint Integration (Optional)

### Create Azure AD App:

1. Go to [Azure Portal](https://portal.azure.com)
2. **Azure Active Directory** → **App registrations** → **New registration**
3. Name: `ESG Hub GitHub Actions`
4. Supported account types: **Single tenant**
5. Click **Register**

### Configure Permissions:

1. Go to **API permissions** → **Add a permission**
2. Select **SharePoint** → **Application permissions**
3. Add: `Sites.ReadWrite.All`
4. Click **Grant admin consent**

### Create Secret:

1. Go to **Certificates & secrets** → **New client secret**
2. Description: `GitHub Actions`
3. Expires: `24 months`
4. Copy the **Value** (not Secret ID)

### Get IDs:

- **Client ID**: From app overview page
- **Client Secret**: From step above
- **Site URL**: Your SharePoint site (e.g., `https://trilegal.sharepoint.com/sites/ESGHub`)

### Add to GitHub Secrets:

Go to your GitHub repository:
- Settings → Secrets → Actions → New repository secret

Add:
- `SHAREPOINT_SITE`
- `SHAREPOINT_CLIENT_ID`
- `SHAREPOINT_CLIENT_SECRET`

---

## 💰 Cost Comparison

### GitHub Actions Version (This):
- GitHub Actions: **FREE** (2000 min/month, you'll use ~300)
- Power Automate: **FREE** (included in M365)
- SharePoint: **FREE** (included in M365)
- Claude API: **₹500-1000/month**
- **Total: ₹500-1000/month**

### Azure Functions Version (Previous):
- Azure Functions: ₹300-500/month
- Azure Storage: ₹50/month
- Power Automate: FREE
- SharePoint: FREE
- Claude API: ₹500-1000/month
- **Total: ₹850-1550/month**

**Savings: ₹350-550/month (40% cheaper!)**

---

## 📊 Monitoring

### Check GitHub Actions:
- **Actions** tab → Select workflow run
- View logs for each step
- Download artifacts for debugging

### Check Power Automate:
- [make.powerautomate.com](https://make.powerautomate.com)
- **My flows** → `ESG_Receive_And_Store`
- View run history

### Check SharePoint:
- Go to ESG_Articles list
- Filter by `ScrapedDate` = Today

---

## 🐛 Troubleshooting

### Workflow fails at "Scrape all sources"
**Solution:** Check source URLs are accessible, reduce timeout

### "No articles found"
**Solution:** Check keywords are loading, verify sources are active

### Power Automate doesn't receive data
**Solution:** Verify webhook URL in GitHub Secrets, check Power Automate trigger

### SharePoint integration fails
**Solution:** Check Azure AD app permissions, verify client secret hasn't expired

---

## 🔄 Daily Operations

### Automatic:
- **6:00 AM IST**: Workflow runs automatically
- **6:05 AM**: Articles in SharePoint
- **6:10 AM**: Email in your inbox

### Manual:
- **Add source**: Update `config/sources.csv`, commit & push
- **Add keyword**: Update `config/keywords.csv`, commit & push
- **Test**: Go to Actions → Run workflow

---

## 📈 Advantages of GitHub Actions

1. **Free Tier**: 2000 minutes/month (you use ~300)
2. **Version Control**: All code in Git
3. **Easy Testing**: Manual workflow dispatch
4. **Better Logs**: Clearer than Azure Portal
5. **No Azure Setup**: Just GitHub + M365
6. **Artifacts**: Download debugging data
7. **Caching**: Pip cache speeds up runs

---

## 🎯 Next Steps

1. ✅ Set up GitHub repository
2. ✅ Add secrets
3. ✅ Create Power Automate flow
4. ✅ Test manually
5. ⏳ Let it run automatically
6. ⏳ Phase 2: Web portal

---

## 📝 Editing Sources & Keywords

### Add New Source:

**Option A: Edit on GitHub**
1. Go to `config/sources.csv`
2. Click **Edit** (pencil icon)
3. Add new row
4. Commit changes

**Option B: Update SharePoint**
1. Go to ESG_Sources list
2. Add new item
3. GitHub Actions will fetch it automatically

### Add New Keyword:

Same process with `config/keywords.csv` or `ESG_Keywords` list

---

## 🔐 Security Notes

- Repository should be **Private**
- Never commit secrets to Git
- Use GitHub Secrets for all sensitive data
- Rotate Azure AD client secret every 24 months
- Review GitHub Actions logs regularly

---

## 📞 Support

- **GitHub Actions Issues**: Check workflow logs
- **Power Automate Issues**: Check flow run history
- **Claude API Issues**: Check Anthropic console

---

**Ready to deploy? Push to GitHub and you're done!** 🚀

