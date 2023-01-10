GD2 Contributing Guide
======================

Thank you for taking an interesting in contributing to Generic Data Display (GD2), an application that uses OpenMCT and a custom json DSL definition to allow users to quickly spin up custom GUIs for displaying real time telemetry/status data.
Please follow the guidlines within to make a commit to GD2 proper.

## Process
The process for updating GD2 involves the following workflow: 
- Create an issue
- Clone the repository
- Create a branch
- Make changes on your branch
- Test locally to ensure no existing tests break
- Create new tests to test functionality
- Ensure docker containers still build and function
- Push to branch
- Create a pull/merge request
- Ensure tests pass in git workflow
- Get approval from a trusted commiter
- Merge your branch
- Resolve your issue