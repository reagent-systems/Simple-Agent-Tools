# Simple-Agent-Tools
This is for the tools/commands that simple agent have access to! 

### Contribution Guidelines

1. **Documentation**: All updates should include necessary documentation updates in the `docs/` folder, especially if they affect existing protocol structures.
2. **Code Reviews**: All new code contributions require code review approval from at least one senior developer.

### Commit References

To link commits to specific GitHub issues, use `#number` in your commit message, where `number` corresponds to the issue ID. This will allow each commit to be traced back to the relevant issue.

Example:

- `Fixes #123` – Links the commit to issue #123, marking it as fixed.
- `Closes #456` – Links the commit to issue #456, closing it upon merge.

### Reserved Keywords

These keywords should be used in commit messages to maintain consistency and automate issue tracking:

- **Resolve**: Use when a commit fixes an issue. Example: `Resolve #123 - Fix null pointer exception`
- **Fix**: For bug fixes. Example: `Fix #234 - Correct date formatting in transaction logs`
- **Close**: When the commit closes an issue entirely. Example: `Close #345 - Add error handling for API timeout`
- **Refactor**: For commits that improve code without changing functionality. Example: `Refactor payment processing logic`
- **Add**: For new features or files. Example: `Add new endpoint for customer data retrieval`
- **Remove**: For deleting files, features, or code. Example: `Remove deprecated transaction processing logic`

### Good Commit Guidelines

1. **Be Descriptive**: Clearly state what the commit accomplishes in a concise manner.
   - Example: `Fix #78 - Correct response format in API for POS transactions`
2. **Use Imperative Mood**: Start with a verb, as if giving a command.
   - Example: `Add support for multi-tenant environment`
3. **Reference Issues**: Use the issue number where applicable (e.g., `Fix #123`).
4. **Separate Concepts**: Make separate commits for different types of changes (e.g., fixes, refactoring).
5. **Keep It Short**: Limit subject lines to 50 characters when possible, followed by a more detailed description if needed.

#### Example Good Commit Messages

- `Fix #203 - Correct timeout handling in API gateway`
- `Add #215 - Integrate Zelle connector with API Fabric`
- `Refactor database access layer for improved security`
- `Document setup process for C2C connectors`

### Bad Commit Guidelines

1. **Avoid Generic Messages**: Don’t use vague messages like “fixed issue” or “updated files”.
   - Bad Example: `Fixed bug`
2. **Avoid Long or Unformatted Messages**: Don’t write multi-sentence summaries in the commit title. Use the title for a concise summary and details in the body if needed.
   - Bad Example: `Made some changes to fix the issue with the API that we found in the last test and improved some of the handling`
3. **Do Not Group Unrelated Changes**: Each commit should address a single issue or feature.
   - Bad Example: `Fix login bug, add new API endpoint, update tests`
4. **Avoid Overly Technical Jargon**: Make the message understandable for anyone reviewing the commit.
   - Bad Example: `Resolved race condition with mutex lock on DB connection pool`
5. **Avoid Irrelevant Details**: Don’t add personal commentary or irrelevant context.
   - Bad Example: `Trying this approach again because the last one didn’t work`

# Commit Often!
