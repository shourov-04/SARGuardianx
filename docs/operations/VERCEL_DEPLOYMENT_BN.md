# Vercel-এ SARGuardian deploy

এই monorepo থেকে একই GitHub repository ব্যবহার করে **দুটি আলাদা Vercel Project** তৈরি হবে:

| Project | Root Directory | Runtime |
|---|---|---|
| Frontend | `apps/dynamic/Frontend` | Vite/React |
| Backend API | `apps/dynamic/Backend` | Python/FastAPI Function |

Scientific processing Vercel Function-এর মধ্যে চলে না। API GitHub Actions workflow dispatch করে; worker private Drive result তৈরি করে API-তে signed callback পাঠায়। এই কারণে Vercel environment variables এবং GitHub Actions secrets দুটোই লাগবে।

বর্তমান handoff: code [migration PR #1](https://github.com/shourov-04/SARGuardian/pull/1)-এ আছে এবং Linux CI pass করেছে। Review শেষে PR `main`-এ merge করুন। Vercel-এর Production Branch হিসেবে `main` ব্যবহার করুন।

## ১. Backend API Project

Vercel Dashboard → Add New → Project থেকে `shourov-04/SARGuardian` import করুন।

- Project name: নিজের পছন্দ; যেমন `sarguardian-api`
- Root Directory: `apps/dynamic/Backend`
- Framework: FastAPI/Python auto-detection ব্যবহার করুন
- Build/Install command: override প্রয়োজন নেই; `requirements.txt` স্বয়ংক্রিয়ভাবে install হবে
- Entrypoint: `index.py`; এটি existing FastAPI `app` export করে
- Python: `.python-version` অনুযায়ী `3.13`
- Production Branch: `main`

`Backend/vercel.json` API function-এর maximum duration `300` seconds করে। Fluid compute চালু রাখুন; current Vercel limits অনুযায়ী Hobby-তেও Fluid compute সহ 300 seconds সমর্থিত। Long-running satellite processing তবুও GitHub Actions-এই থাকবে।

Backend Project-এর Environment Variables-এ দিন:

| Variable | Value / purpose |
|---|---|
| `APP_ENV` | `production` |
| `CORS_ORIGINS` | frontend-এর exact HTTPS origin; একাধিক হলে comma-separated; trailing slash নয় |
| `SUPABASE_URL` | active Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | server-only secret/service-role key |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | একই Firebase project-এর সম্পূর্ণ Admin service-account JSON |
| `GOOGLE_DRIVE_OAUTH_CLIENT_JSON` | private result folder ব্যবহারকারী OAuth client JSON |
| `GOOGLE_DRIVE_REFRESH_TOKEN` | ঐ Drive identity-র refresh token |
| `GOOGLE_DRIVE_FOLDER_ID` | private results folder ID |
| `GITHUB_ACTIONS_TOKEN` | `shourov-04/SARGuardian`-এ Actions read/write এবং Contents read permission-সহ token |
| `GITHUB_ACTIONS_REPOSITORY` | `shourov-04/SARGuardian` |
| `GITHUB_ACTIONS_WORKFLOW` | `sarguardian-displacement.yml` |
| `GITHUB_ACTIONS_REF` | `main` |
| `PUBLIC_API_URL` | API Project-এর production base URL, যেমন `https://sarguardian-api.vercel.app` |
| `DISPLACEMENT_CALLBACK_SECRET` | দীর্ঘ random secret; GitHub-এর একই নামের secret-এর সঙ্গে এক হতে হবে |
| `DISPLACEMENT_ACTIONS_ENABLED` | প্রথমে `false`; schema/secrets/pilot প্রস্তুত হলে `true` |
| `KNOWN_PLACE_REPOSITORY` | `shourov-04/SARGuardian` |
| `KNOWN_PLACE_REF` | `main` |
| `KNOWN_PLACE_PAPER_REPOSITORY` | `shourov-04/SARGuardian` |
| `KNOWN_PLACE_PAPER_REF` | `main` |
| `RIVERSHIFT_GITHUB_ACTIONS_REPOSITORY` | `shourov-04/SARGuardian` |
| `RIVERSHIFT_GITHUB_ACTIONS_WORKFLOW` | `river-shift-gcov-process.yml` |
| `RIVERSHIFT_GITHUB_ACTIONS_REF` | `main` |
| `RIVERSHIFT_CALLBACK_SECRET` | GitHub-এর একই নামের secret-এর সঙ্গে এক হতে হবে |
| `RIVERSHIFT_ACTIONS_ENABLED` | প্রথমে `false`; configuration যাচাইয়ের পরে `true` |

RiverShift সাধারণ `GITHUB_ACTIONS_TOKEN` ও `PUBLIC_API_URL` fallback হিসেবে ব্যবহার করে। আলাদা credential/URL দরকার হলেই `RIVERSHIFT_GITHUB_ACTIONS_TOKEN` ও `RIVERSHIFT_PUBLIC_API_URL` দিন। খালি override তৈরি করবেন না।

Vercel `VERCEL=1` নিজে দেয়, তাই সেটি manually যোগ করবেন না। `PORT` বা local Windows `GOOGLE_APPLICATION_CREDENTIALS` path দেবেন না। Secret কোনো `VITE_*` variable-এ দেবেন না। Environment variable বদলানোর পরে redeploy প্রয়োজন।

## ২. Frontend Project

একই repository আবার import করে দ্বিতীয় Project বানান:

- Project name: যেমন `sarguardian-web`
- Root Directory: `apps/dynamic/Frontend`
- Framework Preset: Vite
- Install Command: `npm ci`
- Build Command: `npm run build`
- Output Directory: `dist`
- Production Branch: `main`

`Frontend/vercel.json` SPA route-গুলোকে `index.html`-এ rewrite করে; `/archive`, `/landslide` বা অন্য client route refresh করলে তাই 404 হবে না।

Frontend Project-এর Environment Variables:

- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_APP_ID`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_MEASUREMENT_ID` — Analytics না থাকলে optional
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_GOOGLE_MAPS_API_KEY` — browser/referrer restricted key
- `VITE_SARGUARDIAN_API_URL` — backend production base URL

`VITE_*` variables browser bundle-এ public হয়। এখানে Supabase service key, Firebase Admin JSON, GitHub token, Drive credential বা callback secret দেবেন না। Variable বদলালে frontend redeploy করুন।

## ৩. GitHub Actions secrets

GitHub → `shourov-04/SARGuardian` → Settings → Secrets and variables → Actions:

| Secret | Purpose |
|---|---|
| `EARTHDATA_TOKEN` | NASA/Earthdata download |
| `EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD` | username/password fallback এবং retry |
| `GOOGLE_DRIVE_OAUTH_CLIENT_JSON` | private result upload |
| `GOOGLE_DRIVE_REFRESH_TOKEN` | একই Drive identity |
| `GOOGLE_DRIVE_PARENT_FOLDER_ID` | Known Place/RiverShift worker folder |
| `GOOGLE_DRIVE_FOLDER_ID` | Dynamic workflow compatibility; একই folder ID দিন |
| `DISPLACEMENT_CALLBACK_SECRET` | Backend Project-এর একই value |
| `RIVERSHIFT_CALLBACK_SECRET` | Backend Project-এর একই value |

Vercel variables GitHub Actions-এ যায় না এবং GitHub secrets Vercel runtime-এ আসে না। API dispatch PAT শুধু Backend Project-এ রাখুন; workflow-এর `GITHUB_TOKEN` GitHub নিজে দেয়।

## ৪. Supabase, Firebase ও Maps

নতুন Supabase project হলে `apps/dynamic/Backend/supabase/migrations/`-এর সাতটি SQL file timestamp অনুযায়ী apply করুন। Existing project হলে migration history মিলিয়ে নিন; duplicate SQL চালাবেন না। এই repository migration কোনো live database-এ SQL চালায়নি।

Firebase Authentication-এ Google provider enable করে final frontend hostname Authorized domains-এ যোগ করুন। Maps JavaScript API ও Places API (New) enable করে browser key-তে final frontend origin-এর referrer restriction দিন। Firebase web variables এবং Admin service-account JSON একই project-এর হতে হবে।

## ৫. Recommended deployment order

1. PR review করে `main`-এ merge করুন।
2. Backend Project তৈরি করে variables দিন; processing switches `false` রাখুন এবং deploy করুন।
3. Backend production URL নিয়ে Frontend Project-এর `VITE_SARGUARDIAN_API_URL` দিন ও deploy করুন।
4. Actual frontend production origin Backend-এর `CORS_ORIGINS`-এ বসিয়ে backend redeploy করুন।
5. Firebase/Maps domain restrictions update করুন।
6. `/health`, sign-in, map/search, AOI, catalogue preflight ও archive route যাচাই করুন।
7. GitHub secrets/schema/permissions যাচাই করে processing switches `true` করুন।
8. ছোট, সম্মত AOI/date window দিয়ে pilot চালিয়ে callback, failure state, Drive result ও dashboard পরীক্ষা করুন।

Vercel non-production branch-এর জন্য Preview Deployment তৈরি করতে পারে। Preview frontend-কে production API ব্যবহার করালে production API-র CORS allowlist-এ preview origin explicitভাবে যোগ করতে হবে। Preview environment-এর variables আলাদাভাবে configure করুন।

এই migration কোনো Vercel Project তৈরি, domain change, database mutation, secret transfer বা live satellite processing করেনি।

Official references: [Vercel monorepos](https://vercel.com/docs/monorepos), [build Root Directory](https://vercel.com/docs/builds/configure-a-build), [Python/FastAPI runtime](https://vercel.com/docs/functions/runtimes/python), [environment variables](https://vercel.com/docs/environment-variables), [function duration](https://vercel.com/docs/functions/configuring-functions/duration).
