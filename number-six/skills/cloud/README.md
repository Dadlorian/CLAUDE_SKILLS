# Cloud Skill: Professional Skill Creator

A meta-skill that helps you create high-quality, professionally descriptive Claude Code skills using proven patterns.

## What It Does

The Cloud skill guides you through creating production-ready skills by:
- Analyzing your requirements
- Recommending appropriate patterns
- Generating complete skill implementations
- Following best practices and conventions

## When to Use

Use this skill when you want to:
- Create a new Claude Code skill from scratch
- Improve an existing skill's structure
- Learn skill design patterns
- Ensure your skill follows best practices

## Skill Patterns Included

The Cloud skill knows 5 proven patterns:

1. **Task Automation** - For repeatable workflows and multi-step processes
2. **Analysis & Review** - For code review, auditing, and quality assessment
3. **Generation & Scaffolding** - For creating new code and project structures
4. **Transformation & Migration** - For refactoring and version upgrades
5. **Interactive Assistant** - For guided, exploratory workflows

## Usage

### Basic Usage

Simply invoke the skill and describe what you want to create:

```
User: I need a skill that helps me set up new microservices
Claude: [Cloud skill activates and guides you through creation]
```

### With Specific Pattern

You can request a specific pattern:

```
User: Create a Generation & Scaffolding skill for React components
Claude: [Generates skill using that pattern]
```

### Iterative Refinement

Start broad and refine:

```
User: Help me create a deployment skill
Claude: I'll help you create a deployment skill. A few questions:
        1. What are you deploying? (frontend, backend, full-stack)
        2. What's your deployment target? (AWS, Vercel, Docker, etc.)
        3. Do you need pre-deployment checks?
        [Continues with guided creation...]
```

## What Gets Generated

When you use the Cloud skill, it creates:

1. **skill.md** - The main skill prompt with detailed instructions
2. **README.md** - User-facing documentation
3. **templates/** - Any template files needed (optional)

## Examples

### Example 1: Creating an API Endpoint Generator

```
User: I want a skill that generates REST API endpoints for my Node.js app

Claude: Perfect! I'll create a Generation & Scaffolding skill for you.
        Let me ask a few questions:

        1. What framework are you using? (Express, Fastify, etc.)
        2. Do you use TypeScript or JavaScript?
        3. Where should generated files be placed?

        [After gathering info, generates complete skill with endpoints,
         controllers, tests, and validation]
```

### Example 2: Creating a Code Review Skill

```
User: Create a skill that reviews Python code for security issues

Claude: I'll create an Analysis & Review skill focused on Python security.
        This skill will check for:
        - SQL injection vulnerabilities
        - XSS risks
        - Unsafe deserialization
        - Hardcoded secrets
        - And more...

        [Generates comprehensive security review skill]
```

## Tips for Best Results

1. **Be Specific**: Describe your exact use case
2. **Provide Context**: Mention your tech stack, conventions, workflow
3. **Iterate**: Start simple, then add complexity
4. **Test**: Try the generated skill on real code and refine

## Advanced Features

### Pattern Combination

The Cloud skill can combine multiple patterns:

```
User: I need a skill that analyzes my API, finds issues, and fixes them

Claude: I'll combine Analysis & Review + Transformation patterns...
        [Creates hybrid skill]
```

### Parameterization

Generated skills can include configuration options:

```markdown
## Configuration
- strictness: "high" | "medium" | "low"
- auto_fix: true | false
- output_format: "markdown" | "json"
```

### Skill Composition

Skills can reference other skills:

```markdown
## Prerequisites
1. Run `code-formatter` skill first
2. Ensure `test-runner` passes
```

## Troubleshooting

**Skill too generic?**
→ Provide more specific requirements and examples

**Need different structure?**
→ Ask to use a different pattern or combine patterns

**Want to modify generated skill?**
→ Ask for specific changes to any section

## Contributing

To improve this skill:
1. Test it with various use cases
2. Note what works well and what doesn't
3. Submit feedback or enhanced patterns
4. Share successful skills you've created

## Related Skills

- `skill-validator` - Validates skill structure and quality
- `skill-tester` - Tests skills with sample inputs
- `skill-optimizer` - Improves existing skill prompts

## License

This skill is part of the CLAUDE_SKILLS repository.
