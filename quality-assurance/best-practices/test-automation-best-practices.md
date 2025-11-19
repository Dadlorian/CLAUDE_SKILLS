# Test Automation Best Practices

## Page Object Model Best Practices

### DO ✅
- Keep page objects focused on one page/component
- Use data-testid attributes for selectors
- Return page objects from methods for chaining
- Handle waits in page object methods
- Make selectors private, methods public

### DON'T ❌
- Put assertions in page objects
- Access elements directly from tests
- Duplicate selectors across page objects
- Use sleep() or arbitrary waits
- Mix concerns (page + test logic)

## Test Data Management

### DO ✅
- Use factories/builders for test data
- Generate unique data per test
- Clean up test data after tests
- Use realistic data (Faker.js)
- Version control test data schemas

### DON'T ❌
- Share test data between tests
- Hardcode magic values
- Leave test data in database
- Use production data directly
- Expose sensitive data in tests

## Assertions

### DO ✅
- Use specific assertions (toBe, toEqual)
- One logical assertion per test
- Test both positive and negative cases
- Use meaningful assertion messages
- Wait for conditions before asserting

### DON'T ❌
- Use vague assertions (toBeTruthy)
- Mix multiple concerns in one test
- Test only happy paths
- Assume timing without waits
- Ignore assertion failures

## Test Organization

### DO ✅
- Group related tests in describe blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent
- Run tests in any order

### DON'T ❌
- Create test dependencies
- Use generic names (test1, test2)
- Mix setup in test body
- Share state between tests
- Rely on execution order
