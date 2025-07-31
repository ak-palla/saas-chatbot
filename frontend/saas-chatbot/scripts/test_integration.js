#!/usr/bin/env node

/**
 * Frontend Integration Testing Script
 * Tests frontend-backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class FrontendIntegrationTester {
  constructor() {
    this.baseUrl = API_BASE_URL;
    this.authToken = null;
    this.userId = null;
    this.testResults = [];
  }

  async logTest(testName, passed, details = '') {
    const result = {
      test: testName,
      passed,
      timestamp: new Date().toISOString(),
      details
    };
    
    this.testResults.push(result);
    
    const status = passed ? '✅' : '❌';
    console.log(`${status} ${testName}${details ? ': ' + details : ''}`);
  }

  async testApiConnection() {
    console.log('🌐 Testing API connection...');
    
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`);
      const data = await response.json();
      
      if (response.ok && data.status === 'healthy') {
        await this.logTest('API Connection', true, 'Health endpoint responding');
        return true;
      } else {
        await this.logTest('API Connection', false, `Status: ${response.status}`);
        return false;
      }
    } catch (error) {
      await this.logTest('API Connection', false, error.message);
      return false;
    }
  }

  async testCorsConfiguration() {
    console.log('🔒 Testing CORS configuration...');
    
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`, {
        method: 'OPTIONS'
      });
      
      const corsHeader = response.headers.get('Access-Control-Allow-Origin');
      if (corsHeader) {
        await this.logTest('CORS Configuration', true, `Allowed origin: ${corsHeader}`);
        return true;
      } else {
        await this.logTest('CORS Configuration', false, 'No CORS headers found');
        return false;
      }
    } catch (error) {
      await this.logTest('CORS Configuration', false, error.message);
      return false;
    }
  }

  async testAuthenticationEndpoints() {
    console.log('🔐 Testing authentication endpoints...');
    
    const endpoints = [
      '/api/v1/auth/me',
      '/api/v1/auth/health'
    ];
    
    let allPassed = true;
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          headers: {
            'Authorization': 'Bearer invalid_token'
          }
        });
        
        // Should return 401 for invalid token
        if (response.status === 401) {
          await this.logTest(`Auth ${endpoint}`, true, 'Returns 401 for invalid token');
        } else {
          await this.logTest(`Auth ${endpoint}`, false, `Expected 401, got ${response.status}`);
          allPassed = false;
        }
      } catch (error) {
        await this.logTest(`Auth ${endpoint}`, false, error.message);
        allPassed = false;
      }
    }
    
    return allPassed;
  }

  async testApiEndpointsStructure() {
    console.log('🔍 Testing API endpoint structure...');
    
    const endpoints = [
      '/api/v1/health',
      '/api/v1/auth/me',
      '/api/v1/chatbots',
      '/api/v1/documents',
      '/api/v1/conversations',
      '/api/v1/billing/subscription',
      '/api/v1/billing/usage'
    ];
    
    let allPassed = true;
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`);
        
        // Should return 200, 401, or 422
        if ([200, 401, 422].includes(response.status)) {
          await this.logTest(`Endpoint ${endpoint}`, true, `Status: ${response.status}`);
        } else {
          await this.logTest(`Endpoint ${endpoint}`, false, `Unexpected status: ${response.status}`);
          allPassed = false;
        }
      } catch (error) {
        await this.logTest(`Endpoint ${endpoint}`, false, error.message);
        allPassed = false;
      }
    }
    
    return allPassed;
  }

  async testErrorHandling() {
    console.log('🚨 Testing error handling...');
    
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/nonexistent`);
      const data = await response.json();
      
      if (response.status === 404 && 'detail' in data) {
        await this.logTest('Error Handling', true, '404 with proper error format');
        return true;
      } else {
        await this.logTest('Error Handling', false, 'Unexpected error format');
        return false;
      }
    } catch (error) {
      await this.logTest('Error Handling', false, error.message);
      return false;
    }
  }

  async testRequestHeaders() {
    console.log('📋 Testing request headers...');
    
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`);
      const headers = response.headers;
      
      const requiredHeaders = ['content-type'];
      let missingHeaders = [];
      
      for (const header of requiredHeaders) {
        if (!headers.has(header)) {
          missingHeaders.push(header);
        }
      }
      
      if (missingHeaders.length === 0) {
        await this.logTest('Request Headers', true, 'All required headers present');
        return true;
      } else {
        await this.logTest('Request Headers', false, `Missing: ${missingHeaders.join(', ')}`);
        return false;
      }
    } catch (error) {
      await this.logTest('Request Headers', false, error.message);
      return false;
    }
  }

  async testEnvironmentVariables() {
    console.log('⚙️ Testing environment variables...');
    
    const requiredEnvVars = [
      'NEXT_PUBLIC_API_URL',
      'NEXT_PUBLIC_SUPABASE_URL',
      'NEXT_PUBLIC_SUPABASE_PUBLISHABLE_OR_ANON_KEY'
    ];
    
    let missingVars = [];
    
    for (const envVar of requiredEnvVars) {
      if (!process.env[envVar]) {
        missingVars.push(envVar);
      }
    }
    
    if (missingVars.length === 0) {
      await this.logTest('Environment Variables', true, 'All required vars present');
      return true;
    } else {
      await this.logTest('Environment Variables', false, `Missing: ${missingVars.join(', ')}`);
      return false;
    }
  }

  async testApiService() {
    console.log('🔗 Testing API service...');
    
    try {
      // Test the API service structure
      const apiService = {
        request: async (endpoint, options = {}) => {
          const url = `${this.baseUrl}${endpoint}`;
          const config = {
            ...options,
            headers: {
              'Content-Type': 'application/json',
              ...options.headers
            }
          };
          
          const response = await fetch(url, config);
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          return response.json();
        }
      };
      
      // Test health endpoint via API service
      const data = await apiService.request('/api/v1/health');
      
      if (data.status === 'healthy') {
        await this.logTest('API Service', true, 'Service structure working');
        return true;
      } else {
        await this.logTest('API Service', false, 'Unexpected response format');
        return false;
      }
    } catch (error) {
      await this.logTest('API Service', false, error.message);
      return false;
    }
  }

  async runAllTests() {
    console.log('🚀 Starting frontend integration tests...');
    console.log(`API Base URL: ${this.baseUrl}`);
    console.log('=' * 50);

    const tests = [
      this.testEnvironmentVariables,
      this.testApiConnection,
      this.testCorsConfiguration,
      this.testAuthenticationEndpoints,
      this.testApiEndpointsStructure,
      this.testErrorHandling,
      this.testRequestHeaders,
      this.testApiService
    ];

    let passed = 0;
    let failed = 0;

    for (const test of tests) {
      try {
        const result = await test();
        if (result) {
          passed++;
        } else {
          failed++;
        }
      } catch (error) {
        await this.logTest(test.name, false, error.message);
        failed++;
      }
    }

    console.log('\n' + '=' * 50);
    console.log(`🎯 Test Results: ${passed}/${passed + failed} passed`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);

    // Save results
    const report = {
      timestamp: new Date().toISOString(),
      baseUrl: this.baseUrl,
      results: this.testResults,
      summary: { passed, failed, total: passed + failed }
    };

    const fs = require('fs');
    fs.writeFileSync('frontend_integration_report.json', JSON.stringify(report, null, 2));
    console.log('\n📊 Test report saved to frontend_integration_report.json');

    return { passed, failed };
  }
}

// CLI runner
async function main() {
  console.log('🔧 Frontend Integration Tester');
  
  const tester = new FrontendIntegrationTester();
  const results = await tester.runAllTests();
  
  process.exit(results.failed > 0 ? 1 : 0);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = FrontendIntegrationTester;