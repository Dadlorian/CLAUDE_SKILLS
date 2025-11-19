# Hands-On Lab Template: Complete Structure

This template provides a comprehensive structure for creating interactive, hands-on labs that complement tutorials.

## Lab Metadata

```yaml
lab_id: "lab_001_example"
title: "Building Your First Application"
subtitle: "A comprehensive hands-on experience"
difficulty_level: "beginner" # beginner, intermediate, advanced
estimated_duration: 45 # minutes
version: "1.0.0"
last_updated: "2025-11-19"
prerequisites:
  - "Understanding of basic programming concepts"
  - "Installed Node.js 16+"
  - "Git installed on your system"
learning_outcomes:
  - "Set up a development environment"
  - "Create and run a basic application"
  - "Debug common issues"
  - "Deploy to a test server"
tags: ["hands-on", "beginner", "development"]
```

## I. Learning Objectives

### Primary Objectives
By completing this lab, you will be able to:

1. **Setup**: Initialize a new project with all necessary dependencies
2. **Implementation**: Write functional code following best practices
3. **Testing**: Validate your code through automated tests
4. **Deployment**: Deploy your application to a staging environment
5. **Troubleshooting**: Diagnose and fix common issues

### Skill Development Areas
- **Technical Skills**: Programming, version control, testing
- **Problem-Solving**: Debugging, research, analysis
- **Communication**: Documentation, error reporting

---

## II. Lab Environment Setup

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 2GB | 4GB+ |
| Disk Space | 500MB | 2GB+ |
| Internet | Required | Required |
| OS | Windows/Mac/Linux | Modern OS |

### Installation Instructions

```bash
# Step 1: Clone the lab repository
git clone https://github.com/example/lab-starter.git
cd lab-starter

# Step 2: Install dependencies
npm install

# Step 3: Verify installation
npm test

# Step 4: Start the development server
npm start
```

### Verification Checklist
- [ ] All dependencies installed without errors
- [ ] `npm test` runs successfully
- [ ] Development server starts on localhost:3000
- [ ] No console errors visible

### Troubleshooting Common Setup Issues

**Issue**: `npm: command not found`
- **Solution**: Node.js not installed. Download from nodejs.org

**Issue**: Port 3000 already in use
- **Solution**: Run `npm start -- --port 3001` to use alternative port

**Issue**: Permission denied errors
- **Solution**: Use `sudo npm install` (Mac/Linux) or run as administrator (Windows)

---

## III. Lab Modules

### Module 1: Foundation Setup (15 minutes)

#### 1.1 Project Initialization

**Objective**: Create the project structure and understand project organization.

**Instructions**:
1. Navigate to your lab workspace
2. Create the following directory structure:
   ```
   my-app/
   ├── src/
   │   ├── components/
   │   ├── utils/
   │   └── index.js
   ├── tests/
   ├── public/
   └── package.json
   ```

3. Initialize Git repository
   ```bash
   cd my-app
   git init
   git add .
   git commit -m "Initial project structure"
   ```

**Verification**:
```bash
# Run verification script
npm run verify:module-1
```

Expected output:
```
✓ Directory structure is correct
✓ Git repository initialized
✓ .gitignore present
✓ Module 1: PASSED
```

**Checkpoint Questions**:
1. Why do we organize code into separate directories?
2. What does `.gitignore` do and what files should be excluded?
3. Explain the purpose of `package.json`

---

#### 1.2 Environment Configuration

**Objective**: Set up environment variables and configuration files.

**Instructions**:
1. Create `.env.example` file:
   ```
   API_URL=https://api.example.com
   DEBUG=false
   PORT=3000
   ```

2. Create local `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your local settings

4. Create `config.js`:
   ```javascript
   module.exports = {
     apiUrl: process.env.API_URL,
     debug: process.env.DEBUG === 'true',
     port: process.env.PORT || 3000
   };
   ```

**Common Mistake**: Committing `.env` to version control
- Always add `.env` to `.gitignore`
- Use `.env.example` as a template

**Verification**:
```bash
npm run verify:env-setup
```

---

### Module 2: Core Implementation (20 minutes)

#### 2.1 Building the Main Component

**Objective**: Implement the core functionality of the application.

**Instructions**:

1. Create `src/index.js`:
   ```javascript
   const config = require('./config');

   class Application {
     constructor() {
       this.config = config;
       this.initialized = false;
     }

     async initialize() {
       console.log('Initializing application...');
       // Your initialization code here
       this.initialized = true;
       console.log('Application ready!');
     }

     run() {
       if (!this.initialized) {
         throw new Error('Application not initialized');
       }
       // Your main logic here
     }
   }

   module.exports = Application;
   ```

2. Create `src/utils/helpers.js`:
   ```javascript
   function validateInput(input, rules) {
     // Validation logic
     return true;
   }

   function formatOutput(data) {
     // Formatting logic
     return data;
   }

   module.exports = { validateInput, formatOutput };
   ```

3. Create `src/components/DataProcessor.js`:
   ```javascript
   class DataProcessor {
     constructor(config) {
       this.config = config;
     }

     process(data) {
       if (!Array.isArray(data)) {
         throw new Error('Input must be an array');
       }

       return data.map(item => ({
         ...item,
         processed: true,
         timestamp: new Date().toISOString()
       }));
     }
   }

   module.exports = DataProcessor;
   ```

**Code Quality Checklist**:
- [ ] Code follows naming conventions (camelCase for variables, PascalCase for classes)
- [ ] Functions have clear purposes with single responsibility
- [ ] Comments explain "why" not "what"
- [ ] Error handling is implemented

**Verification**:
```bash
npm run verify:implementation
npm run lint
npm run test
```

---

#### 2.2 Integration Testing

**Objective**: Ensure modules work together correctly.

**Instructions**:

1. Create `tests/integration.test.js`:
   ```javascript
   const Application = require('../src/index');
   const DataProcessor = require('../src/components/DataProcessor');

   describe('Application Integration', () => {
     let app;

     beforeEach(async () => {
       app = new Application();
       await app.initialize();
     });

     test('should initialize successfully', () => {
       expect(app.initialized).toBe(true);
     });

     test('should process data correctly', () => {
       const processor = new DataProcessor(app.config);
       const input = [{ id: 1, name: 'Test' }];
       const result = processor.process(input);

       expect(result[0]).toHaveProperty('processed', true);
       expect(result[0]).toHaveProperty('timestamp');
     });
   });
   ```

2. Run tests:
   ```bash
   npm test
   ```

---

### Module 3: Debugging and Troubleshooting (10 minutes)

#### 3.1 Debugging Techniques

**Objective**: Learn to identify and fix bugs effectively.

**Common Issues and Solutions**:

| Issue | Symptom | Solution |
|-------|---------|----------|
| Undefined variable | `TypeError: X is undefined` | Check variable scope and initialization |
| Async/await problems | Promise rejection not handled | Use `.catch()` or try/catch blocks |
| Configuration errors | `Cannot read property of undefined` | Verify .env file and config loading |
| Module not found | `Cannot find module 'X'` | Run `npm install` and check import paths |

**Debugging Tools**:

```javascript
// 1. Console logging
console.log('Debug info:', variable);
console.table(arrayOfObjects);

// 2. Debugger statement
debugger; // Execution pauses here when dev tools open

// 3. Error stack traces
try {
  // Code
} catch (error) {
  console.error('Error:', error.message);
  console.error('Stack:', error.stack);
}

// 4. Unit tests as debugging
// Tests help isolate issues by testing components individually
```

**Lab Exercise - Find and Fix Bugs**:

You'll receive code with intentional bugs. Debug and fix them:

```javascript
// Bug: Missing error handling
function calculateTotal(prices) {
  return prices.reduce((sum, price) => sum + price);
}

// Fixed version:
function calculateTotal(prices) {
  if (!Array.isArray(prices)) {
    throw new Error('Prices must be an array');
  }
  return prices.reduce((sum, price) => {
    if (typeof price !== 'number') {
      throw new Error('All prices must be numbers');
    }
    return sum + price;
  }, 0);
}
```

**Verification**:
```bash
npm run debug:challenge
```

---

### Module 4: Deployment and Validation (8 minutes)

#### 4.1 Prepare for Deployment

**Objective**: Ready your application for production environment.

**Pre-deployment Checklist**:
- [ ] All tests passing (`npm test`)
- [ ] No linting errors (`npm run lint`)
- [ ] Environment variables documented
- [ ] Error handling implemented throughout
- [ ] Performance optimized
- [ ] Security review completed

#### 4.2 Build and Deploy

**Instructions**:

1. Create production build:
   ```bash
   npm run build
   ```

2. Test production build locally:
   ```bash
   npm run serve:build
   ```

3. Deploy to staging:
   ```bash
   npm run deploy:staging
   ```

4. Run final verification:
   ```bash
   npm run verify:deployment
   ```

**Expected Output**:
```
✓ Build successful (1.2MB)
✓ No runtime errors
✓ All endpoints responding
✓ Performance metrics acceptable
✓ Deployment: SUCCESS
```

---

## IV. Advanced Challenges

### Challenge 1: Feature Implementation (Bonus)

Implement an additional feature:
- Add user authentication
- Implement data caching
- Create an API endpoint
- Add real-time notifications

**Success Criteria**:
- Feature is functional
- Tests pass (80%+ coverage)
- Documentation updated

### Challenge 2: Performance Optimization

Identify and optimize performance bottlenecks:
- Profile your application
- Reduce bundle size
- Optimize database queries
- Implement caching strategies

**Success Criteria**:
- 20% performance improvement
- Documented optimization techniques

### Challenge 3: Security Hardening

Implement security best practices:
- Input validation
- SQL injection prevention
- XSS protection
- Secure error handling

**Success Criteria**:
- No security vulnerabilities found
- Security practices documented

---

## V. Deliverables and Submission

### Required Deliverables

1. **Working Application**
   - Fully functional code
   - All tests passing
   - Clean repository with meaningful commits

2. **Documentation**
   - README.md with setup and usage instructions
   - Inline code comments
   - Architecture diagram
   - Troubleshooting guide

3. **Test Suite**
   - Unit tests (80%+ coverage)
   - Integration tests
   - Test documentation

4. **Reflection Document**
   - What you learned
   - Challenges faced and solutions
   - Concepts you want to explore further
   - Code quality self-assessment

### Submission Format

```
lab_submission/
├── src/
├── tests/
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── TROUBLESHOOTING.md
├── .env.example
├── package.json
└── REFLECTION.md
```

### Grading Rubric

| Criterion | Excellent | Good | Needs Work |
|-----------|-----------|------|-----------|
| Functionality | All features work correctly | Minor bugs | Major issues |
| Code Quality | Clean, well-organized, DRY | Generally good | Needs refactoring |
| Testing | 90%+ coverage, all passing | 70%+ coverage | Minimal tests |
| Documentation | Comprehensive, clear | Adequate | Incomplete |
| Problem-Solving | Overcomes obstacles creatively | Resolves issues | Struggles |

---

## VI. Additional Resources

### Documentation
- [Complete API Reference](./api-reference.md)
- [Architecture Guide](./architecture-guide.md)
- [Best Practices](./best-practices.md)

### External Resources
- Official Documentation: [link]
- Tutorial Series: [link]
- Community Forum: [link]

### Getting Help

1. **Review Troubleshooting Guide**: `/docs/TROUBLESHOOTING.md`
2. **Check FAQs**: [link]
3. **Search Community**: [link]
4. **Contact Instructors**: Via learning platform

---

## VII. Lab Completion Checklist

- [ ] All modules completed
- [ ] All verification tests passing
- [ ] Code committed with meaningful messages
- [ ] Documentation complete and accurate
- [ ] No console errors or warnings
- [ ] Reflection document submitted
- [ ] Peer review completed (if applicable)
- [ ] Lab submitted before deadline

**Estimated Time**: 45 minutes
**Total Possible Points**: 100
