# Quick Start

Get started with Project in just 5 minutes.

## Step 1: Install

=== "npm"

    ```bash
    npm install @project/sdk
    ```

=== "pip"

    ```bash
    pip install project-sdk
    ```

=== "Docker"

    ```bash
    docker run -it project/sdk:latest
    ```

## Step 2: Initialize

=== "JavaScript"

    ```javascript
    const Project = require('@project/sdk');

    const client = new Project.Client({
      apiKey: 'your_api_key_here',
    });
    ```

=== "Python"

    ```python
    import project_sdk

    client = project_sdk.Client(
        api_key='your_api_key_here'
    )
    ```

## Step 3: Make Your First Request

=== "JavaScript"

    ```javascript
    async function main() {
      try {
        const user = await client.users.create({
          name: 'John Doe',
          email: 'john@example.com',
        });
        console.log('User created:', user);
      } catch (error) {
        console.error('Error:', error);
      }
    }

    main();
    ```

=== "Python"

    ```python
    try:
        user = client.users.create(
            name='John Doe',
            email='john@example.com'
        )
        print('User created:', user)
    except Exception as e:
        print('Error:', e)
    ```

## Step 4: Verify Success

You should see output like:

```json
{
  "id": "user_123abc",
  "name": "John Doe",
  "email": "john@example.com",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

## Next Steps

- Read [Core Concepts](../concepts/architecture.md)
- Explore [API Reference](../api/overview.md)
- Follow a [Complete Guide](../guides/rest-integration.md)
- Review [Deployment Options](../deployment/overview.md)

---

!!! info "Need Help?"
    Check the [FAQ](../reference/faq.md) or visit our [Discord community](https://discord.gg/example)
