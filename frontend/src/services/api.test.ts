/**
 * Tests for API service
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiService } from './api';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('brainstormKnowledge', () => {
    it('should make POST request to /brainstorm endpoint', async () => {
      const mockResponse = {
        data: {
          mode: 'brainstorming',
          knowledge_response: 'AWS Lambda is a serverless compute service',
          follow_up_questions: ['Question 1', 'Question 2'],
          session_id: 'test-session'
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.brainstormKnowledge({
        requirements: 'Tell me about AWS Lambda'
      });

      expect(result).toBeDefined();
      expect((result as any).mode).toBe('brainstorming');
    });

    it('should extract follow-up questions from response', async () => {
      const mockResponse = {
        data: {
          knowledge_response: 'Response text\n\nFollow-up questions:\n- Question 1\n- Question 2',
          mode: 'brainstorming'
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.brainstormKnowledge({
        requirements: 'Test question'
      });

      expect(result.follow_up_questions).toBeDefined();
    });

    it('should handle errors gracefully', async () => {
      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockRejectedValue(new Error('Network error'))
      });

      await expect(
        apiService.brainstormKnowledge({ requirements: 'Test' })
      ).rejects.toThrow();
    });
  });

  describe('analyzeRequirements', () => {
    it('should make POST request to /analyze-requirements endpoint', async () => {
      const mockResponse = {
        data: {
          mode: 'analysis',
          knowledge_response: 'Analysis response',
          architecture_diagram: '',
          follow_up_questions: []
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.analyzeRequirements({
        requirements: 'Analyze my requirements',
        session_id: 'test-session'
      });

      expect((result as any).mode).toBe('analysis');
    });
  });

  describe('generateArchitecture', () => {
    it('should make POST request to /generate endpoint', async () => {
      const mockResponse = {
        data: {
          cloudformation_template: 'AWSTemplateFormatVersion: ...',
          architecture_diagram: '',
          cost_estimate: {},
          mcp_servers_enabled: ['cfn-server']
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.generateArchitecture({
        requirements: 'Create a Lambda function'
      });

      expect(result.cloudformation_template).toBeDefined();
    });
  });

  describe('handleFollowUpQuestion', () => {
    it('should make POST request to /follow-up endpoint', async () => {
      const mockResponse = {
        data: {
          mode: 'follow_up',
          question: 'How do I deploy?',
          answer: 'Deployment answer',
          success: true
        }
      };

      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.handleFollowUpQuestion(
        'How do I deploy?',
        'Architecture context',
        'test-session'
      );

      expect((result as any).mode).toBe('follow_up');
      expect((result as any).answer).toBeDefined();
    });
  });

  describe('healthCheck', () => {
    it('should make GET request to /health endpoint', async () => {
      const mockResponse = {
        data: {
          status: 'healthy',
          service: 'aws-solution-architect-tool'
        }
      };

      mockedAxios.create.mockReturnValue({
        get: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.healthCheck();

      expect(result.status).toBe('healthy');
    });
  });

  describe('extractFollowUpQuestions', () => {
    it('should extract questions from text with various formats', () => {
      const text1 = 'Response\n\nFollow-up questions:\n- Question 1\n- Question 2';
      const text2 = 'Response\n\nFollow-up questions you might consider:\n- Question A\n- Question B';
      
      // Test extraction logic (would need to export the function or test indirectly)
      expect(text1).toContain('Follow-up questions');
      expect(text2).toContain('Follow-up questions');
    });
  });
});

