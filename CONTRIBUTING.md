# Contributing

Thanks for your interest in contributing to Pollution Anomaly Detection.

Contributions are welcome, whether you want to fix a bug, improve the frontend, add tests, improve documentation, or work on a new feature.

## Getting Started

Before starting work, check the open GitHub Issues.

Issues labeled `good first issue` are intended to be approachable for new contributors.

If you want to work on an issue, leave a comment so others know that it is being worked on.

## Development Workflow

1. Fork the repository.

2. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/pollution.git
cd pollution
```

3. Create a branch for your change:

```bash
git checkout -b feature/your-feature-name
```

For fixes, a branch such as this is also appropriate:

```bash
git checkout -b fix/your-fix-name
```

4. Make your changes.

5. Run the relevant tests and checks.

6. Commit your changes with a clear commit message.

7. Push your branch to your fork.

8. Open a pull request against `main`.

## Backend Setup

Create a Python virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project:

```bash
pip install -e .
```

Run the backend tests:

```bash
pytest
```

All existing tests should pass before opening a pull request.

## Frontend Setup

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

Before opening a pull request containing frontend changes, verify the production build:

```bash
npm run build
```

## Copernicus Credentials

Some functionality requires access to the Copernicus Data Space Ecosystem.

Create a `.env` file in the project root when credentials are required:

```text
COPERNICUS_CLIENT_ID=your_client_id
COPERNICUS_CLIENT_SECRET=your_client_secret
```

Never commit API credentials, tokens, secrets, or your `.env` file.

Many frontend, documentation, refactoring, and test contributions can be developed without making Copernicus API requests.

## Pull Requests

Keep pull requests focused on one issue or change whenever possible.

A pull request should:

- Clearly describe what was changed
- Reference the related issue when applicable
- Include tests for new backend behavior where appropriate
- Keep unrelated changes out of the pull request
- Pass the backend tests and/or frontend build relevant to the change

You can link a pull request to an issue using:

```text
Closes #3
```

When the pull request is merged, GitHub will automatically close the linked issue.

## Reporting Bugs

When reporting a bug, please include:

- What you expected to happen
- What actually happened
- Steps to reproduce the problem
- Relevant error messages or screenshots
- Your environment when relevant

## Feature Ideas

Feature suggestions are welcome.

For larger changes, please open an issue before implementing the feature so the approach can be discussed first.

## Code Style

Try to follow the style and structure already used in the project.

Prefer:

- Small, focused functions
- Clear names
- Type annotations where appropriate
- Tests for backend behavior
- Reusable TypeScript types and components
- Readable code over unnecessary complexity

## Questions

If something about an issue or the project is unclear, feel free to ask a question directly in the relevant GitHub Issue.