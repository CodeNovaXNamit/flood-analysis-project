# Welcome to Antigravity!

Welcome to your new developer home! Your Firebase Studio project has been successfully migrated to Antigravity.

Antigravity is our next-generation, agent-first IDE designed for high-velocity, autonomous development. Because Antigravity runs locally on your machine, you now have access to powerful local workflows and fully integrated AI editing capabilities that go beyond a cloud-based web IDE.

## Getting Started
- **Run Locally**: Use the **Run and Debug** menu on the left sidebar to start your local development server.
  - Or in a terminal run `npm run dev` and visit `http://localhost:9002`.
- **Deploy**: You can deploy your changes to Firebase App Hosting by using the integrated terminal and standard Firebase CLI commands, just as you did in Firebase Studio.
- **Cleanup**: Cleanup unused artifacts with the @cleanup workflow.

Enjoy the next era of AI-driven development!

File any bugs at https://github.com/firebase/firebase-tools/issues

**Firebase Studio Export Date:** 2026-03-28


---

## Previous README.md contents:

# Delhi Flood Frontend

This frontend is a Next.js application for the Delhi ward flood-risk dashboard.

## Data Source

The ward boundary map now uses [`data/Delhi_Wards_with_rebalanced_risk.geojson`](/D:/17.%20Hackathon/Project/flood-analysis-project/frontend/data/Delhi_Wards_with_rebalanced_risk.geojson) as the source dataset.

For bundling in the client app, that file is mirrored into [`src/app/data/Delhi_Wards_with_rebalanced_risk.json`](/D:/17.%20Hackathon/Project/flood-analysis-project/frontend/src/app/data/Delhi_Wards_with_rebalanced_risk.json), and [`src/app/data/mockGeoJSON.ts`](/D:/17.%20Hackathon/Project/flood-analysis-project/frontend/src/app/data/mockGeoJSON.ts) remaps its fields into the app's `WardProperties` shape.

## Local Development

1. Install dependencies:

```bash
npm install
```

2. Start the dev server:

```bash
npm run dev
```

3. Open `http://localhost:9002`.

## Production Build

Run a production build before deploying:

```bash
npm run build
```

To serve the production build locally:

```bash
npm run start
```

## Firebase App Hosting Deployment

This project includes [`apphosting.yaml`](/D:/17.%20Hackathon/Project/flood-analysis-project/frontend/apphosting.yaml) and [`studio.json`](/D:/17.%20Hackathon/Project/flood-analysis-project/frontend/studio.json), so the intended deploy target is Firebase App Hosting.

1. Install the Firebase CLI if it is not already installed:

```bash
npm install -g firebase-tools
```

2. Log in to Firebase:

```bash
firebase login
```

3. Confirm the Firebase project ID from [`studio.json`](/D:/17.%20Hackathon/Project/flood-analysis-project/frontend/studio.json).

Current project ID:
`studio-9459786371-60b27`

4. If needed, select the project:

```bash
firebase use studio-9459786371-60b27
```

5. Deploy from this frontend directory using Firebase App Hosting.

If the backend has already been created in Firebase, deploy it with the Firebase CLI command your project is configured to use. A safe workflow is:

```bash
npm run build
firebase deploy
```

If `firebase deploy` reports that App Hosting is not initialized yet, create/select the App Hosting backend in the Firebase console first, then rerun the deploy command.

## Notes

- The repository currently has local uncommitted changes in multiple files. Review `git status` before committing or deploying.
- The map layer expects ward properties from the rebalanced dataset to include `Ward_Name`, `Ward_No`, and `risk`.
