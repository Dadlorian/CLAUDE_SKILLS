# Claude Code Skills Structure

This repository contains custom skills for Claude Code. Skills extend Claude's capabilities with specialized prompts and workflows.

## Skill Structure

Each skill is organized in its own folder with the following structure:

```
skill-name/
├── skill.md          # Main skill prompt and instructions
├── README.md         # Documentation for the skill (optional)
└── templates/        # Template files used by the skill (optional)
```

### skill.md Format

The `skill.md` file contains the prompt that Claude will use when the skill is invoked. It should include:

1. **Purpose**: Clear description of what the skill does
2. **Instructions**: Step-by-step guidance for Claude to follow
3. **Patterns**: Different approaches or patterns the skill can use
4. **Examples**: Sample inputs and expected outputs
5. **Output Format**: How results should be structured

## Invoking Skills

Skills can be invoked using the Skill tool:
- In conversation: Ask Claude to use a specific skill by name
- Direct invocation: Claude will automatically use relevant skills based on context

## Skill Categories

### Development Skills
- Code generation and refactoring
- Testing and validation
- Documentation generation

### Automation Skills
- Build and deployment workflows
- Configuration management
- Project scaffolding

### Analysis Skills
- Code review and auditing
- Performance analysis
- Architecture documentation

## Creating New Skills

When creating a new skill:

1. Choose a descriptive folder name (lowercase, hyphenated)
2. Create a comprehensive `skill.md` with clear instructions
3. Define multiple patterns or approaches when applicable
4. Include examples to guide Claude's behavior
5. Test the skill with various inputs to ensure consistency

## Best Practices

- **Be Specific**: Provide detailed instructions rather than vague guidance
- **Use Patterns**: Define multiple approaches for flexibility
- **Include Context**: Help Claude understand when to use each pattern
- **Validate Output**: Specify quality criteria and validation steps
- **Iterate**: Refine skills based on actual usage patterns
