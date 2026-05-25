# GitHub Actions Setup - Quick Checklist

## ✅ Prerequisites
- [ ] GitHub account
- [ ] Microsoft 365 with SharePoint (for Power Automate)
- [ ] Anthropic API key ([Get one](https://console.anthropic.com))

---

## 📝 Setup Steps (30 Minutes Total)

### 1. GitHub Repository (5 mins)
- [ ] Create private repository: `esg-intelligence-hub`
- [ ] Upload all files from this folder
- [ ] Verify files are in correct structure:
  ```
  .github/workflows/daily-esg-scraper.yml
  scripts/*.py
  config/*.csv
  requirements.txt
  README.md
  ```

---

### 2. GitHub Secrets (5 mins)

Go to: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**Required (Must Have):**
- [ ] `ANTHROPIC_API_KEY`
  - Value: `sk-ant-api03-...` (your Claude API key)

- [ ] `POWER_AUTOMATE_WEBHOOK`
  - Value: `https://prod-XX.region.logic.azure.com:443/workflows/...`
  - (You'll get this from Power Automate in Step 3)

**Optional (For SharePoint Integration):**
- [ ] `SHAREPOINT_SITE`
  - Value: `https://trilegal.sharepoint.com/sites/ESGHub`

- [ ] `SHAREPOINT_CLIENT_ID`
  - Value: Azure AD App Client ID

- [ ] `SHAREPOINT_CLIENT_SECRET`
  - Value: Azure AD App Secret

> **Note:** If you skip SharePoint secrets, system uses local CSV files (still works great!)

---

### 3. Power Automate Flow (15 mins)

#### Create Flow:
- [ ] Go to [make.powerautomate.com](https://make.powerautomate.com)
- [ ] Click **+ Create** → **Automated cloud flow**
- [ ] Name: `ESG_Receive_And_Store`
- [ ] Trigger: **When a HTTP request is received**

#### Configure HTTP Trigger:
- [ ] Add this JSON schema (copy from README.md)
- [ ] **Save** the flow
- [ ] **Copy the HTTP URL** that appears
- [ ] Add URL to GitHub Secrets as `POWER_AUTOMATE_WEBHOOK`

#### Add Flow Steps:
- [ ] **Initialize variable** - `varAllArticles` (Array)
- [ ] **Apply to each** - `triggerBody()?['articles']`
  - [ ] **SharePoint - Create item** in `ESG_Articles` list:
    - Title: `item()?['title']`
    - SourceURL: `item()?['link']`
    - SourceName: `item()?['source']`
    - AISummary: `item()?['ai_summary']`
    - ArticleCategory: `item()?['category']`
    - RelevanceScore: `item()?['relevance_score']`
    - MatchedKeywords: `string(item()?['matched_keywords'])`
    - ArticleStatus: `New`
    - ScrapedDate: `utcNow()`
- [ ] **Get items** from `Digest_Recipients` (IsActive = Yes)
- [ ] **Apply to each** recipient:
  - [ ] **Compose** HTML email (use template)
  - [ ] **Send email** (Office 365 Outlook)
- [ ] **Save** flow

---

### 4. SharePoint Lists (10 mins)

**If you have SharePoint access:**
- [ ] Run PowerShell script from original package:
  ```powershell
  cd sharepoint-setup
  ./setup-sharepoint-lists.ps1
  ```
- [ ] Import keywords CSV
- [ ] Import sources CSV
- [ ] Add yourself to `Digest_Recipients`

**If you don't have SharePoint admin:**
- [ ] System will use local CSV files (config/keywords.csv, config/sources.csv)
- [ ] Still works! Just edit CSV files to add sources/keywords

---

### 5. Test Run (5 mins)

#### Manual Trigger:
- [ ] Go to your GitHub repository
- [ ] Click **Actions** tab
- [ ] Select "Daily ESG News Scraper"
- [ ] Click **Run workflow** → **Run workflow**
- [ ] Wait 5-10 minutes

#### Verify:
- [ ] Check Actions tab - all steps should be green ✓
- [ ] Check Power Automate - flow should have run
- [ ] Check SharePoint `ESG_Articles` - new items should appear
- [ ] Check your email - digest should arrive

---

## 🎉 Done!

If all steps are ✓, your system is now:
- ✅ Running automatically at 6 AM IST daily
- ✅ Scraping 17 sources
- ✅ Filtering with 180+ keywords
- ✅ AI summarizing with Claude
- ✅ Storing in SharePoint
- ✅ Sending email digests

---

## 🔧 Troubleshooting

### ❌ GitHub Actions fails

**Check:**
- [ ] All secrets are set correctly
- [ ] `requirements.txt` is in root folder
- [ ] Python syntax is correct
- [ ] Check error logs in Actions tab

### ❌ No articles found

**Check:**
- [ ] Keywords CSV is populated
- [ ] Sources CSV is populated
- [ ] Source URLs are accessible
- [ ] Keywords match article content

### ❌ Power Automate doesn't receive data

**Check:**
- [ ] Webhook URL in GitHub Secrets is correct
- [ ] Power Automate trigger is HTTP (not manual)
- [ ] Flow is turned ON

### ❌ Email doesn't send

**Check:**
- [ ] Outlook connector is authenticated
- [ ] Recipient email in `Digest_Recipients` list
- [ ] Email template HTML is valid

---

## 📊 Daily Monitoring

### GitHub Actions:
- Check: **Actions** tab
- Look for: Green checkmarks
- If failed: Click on run → View logs

### Power Automate:
- Check: [Flow run history](https://make.powerautomate.com)
- Look for: Succeeded runs
- If failed: Click on run → View details

### Email:
- Check: Your inbox at ~6:10 AM IST
- Look for: "ESG Intelligence Digest"
- If missing: Check spam folder

---

## 🔄 Making Changes

### Add New Source:
1. Edit `config/sources.csv` on GitHub
2. Add new row with source details
3. Commit changes
4. Next run will include new source

### Add New Keyword:
1. Edit `config/keywords.csv` on GitHub
2. Add new row with keyword details
3. Commit changes
4. Next run will use new keyword

### Change Schedule:
1. Edit `.github/workflows/daily-esg-scraper.yml`
2. Modify `cron:` value (line 6)
3. Commit changes

---

## 💰 Cost Tracking

- GitHub Actions: **FREE** (you use ~300 min/month of 2000 free)
- Power Automate: **FREE** (included in M365)
- SharePoint: **FREE** (included in M365)
- Claude API: **~₹500-1000/month** (track at console.anthropic.com)

**Total: ~₹500-1000/month**

---

## 📈 Success Metrics

### Week 1:
- [ ] System runs daily without failures
- [ ] Receiving consistent email digests
- [ ] 20-50 articles/day processed

### Month 1:
- [ ] Zero manual interventions needed
- [ ] Article quality >80% relevant
- [ ] Team satisfied with digest

---

## 🎯 Next Steps

Once Phase 1 is stable:
- [ ] Phase 2: Build web portal (Next.js)
- [ ] Add user preference management
- [ ] Implement bookmarking
- [ ] Add search & filtering
- [ ] Mobile app (optional)

---

**Need Help?**

- **GitHub Actions**: Check workflow YAML syntax
- **Power Automate**: Review flow run history
- **Claude API**: Check Anthropic console
- **General**: Review README.md

---

**System Status:**

- [ ] Phase 1: Complete ✓
- [ ] Running automatically
- [ ] Email digests working
- [ ] Ready for Phase 2

**Congratulations! Your ESG Intelligence Hub is live! 🎉**

