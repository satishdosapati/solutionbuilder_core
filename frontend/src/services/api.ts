import axios from 'axios';
import { GenerationRequest, GenerationResponse, FollowUpRequest } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Extract follow-up questions from response text
const extractFollowUpQuestions = (text: string): string[] => {
  // Try multiple patterns to catch different formats
  const patterns = [
    // Pattern 1: "Follow-up questions you might consider:" followed by bullet points
    /Follow-up questions you might consider:\s*\n((?:- .+\n?)+)/i,
    // Pattern 2: "Follow-up questions:" followed by bullet points
    /Follow-up questions:\s*\n((?:- .+\n?)+)/i,
    // Pattern 3: Just bullet points after a line break
    /\n((?:- .+\n?)+)$/i,
    // Pattern 4: Questions with different bullet styles
    /Follow-up questions you might consider:\s*\n((?:\* .+\n?)+)/i
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      const questionsText = match[1];
      const questions = questionsText
        .split('\n')
        .map(line => line.replace(/^[-*]\s*/, '').trim())
        .filter(question => question.length > 0);
      
      if (questions.length > 0) {
        console.log('Extracted follow-up questions:', questions);
        return questions;
      }
    }
  }
  
  console.log('No follow-up questions found in text');
  return [];
};

// Clean response text by removing follow-up questions section
const cleanResponseText = (text: string): string => {
  // Try multiple patterns to remove follow-up questions
  const patterns = [
    /Follow-up questions you might consider:\s*\n((?:- .+\n?)+)/i,
    /Follow-up questions:\s*\n((?:- .+\n?)+)/i,
    /\n((?:- .+\n?)+)$/i,
    /Follow-up questions you might consider:\s*\n((?:\* .+\n?)+)/i
  ];
  
  let cleanedText = text;
  for (const pattern of patterns) {
    cleanedText = cleanedText.replace(pattern, '').trim();
  }
  
  return cleanedText;
};

export const apiService = {
  async getAvailableRoles(): Promise<string[]> {
    const response = await api.get('/roles');
    return response.data.roles;
  },

  async getMcpServersForRoles(roles: string[], requirements: string) {
    const response = await api.post('/roles/mcp-servers', {
      roles,
      requirements,
    });
    return response.data;
  },

  async brainstormKnowledge(request: GenerationRequest) {
    try {
      console.log('Making brainstorm API call:', request);
      const response = await api.post('/brainstorm', request);
      console.log('Brainstorm API response:', response.data);
      
      // Extract follow-up questions from the response
      const result = response.data;
      if (result.knowledge_response) {
        result.follow_up_questions = extractFollowUpQuestions(result.knowledge_response);
        result.knowledge_response = cleanResponseText(result.knowledge_response);
      }
      
      return result;
    } catch (error) {
      console.error('Brainstorm API error:', error);
      throw error;
    }
  },

  // Streaming version for real-time responses
  async brainstormKnowledgeStream(request: GenerationRequest, onChunk: (chunk: string) => void) {
    try {
      console.log('Starting streaming request to:', `${API_BASE_URL}/stream-response`);
      const response = await fetch(`${API_BASE_URL}/stream-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requirements: request.requirements,
          mode: 'brainstorm'
        })
      });

      console.log('Streaming response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      const decoder = new TextDecoder();
      let result = '';
      let buffer = '';

      try {
        console.log('Starting to read streaming response...');
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log('Streaming completed');
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          console.log('Received chunk:', chunk.substring(0, 100) + '...');
          buffer += chunk;
          
          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line in buffer
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                console.log('Parsed streaming data:', data);
                if (data.content) {
                  result += data.content;
                  onChunk(data.content);
                }
                if (data.done) {
                  console.log('Streaming done signal received');
                  return {
                    knowledge_response: cleanResponseText(result),
                    follow_up_questions: extractFollowUpQuestions(result),
                    mode: 'brainstorming',
                    success: true
                  };
                }
                if (data.error) {
                  console.error('Streaming error received:', data.error);
                  throw new Error(data.error);
                }
              } catch (e) {
                console.warn('Failed to parse streaming data:', e, 'Line:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      return {
        knowledge_response: cleanResponseText(result),
        follow_up_questions: extractFollowUpQuestions(result),
        mode: 'brainstorming',
        success: true
      };
    } catch (error) {
      console.error('Streaming error:', error);
      throw error;
    }
  },

  async analyzeRequirements(requirements: string) {
    const response = await api.post('/analyze-requirements', {
      requirements,
    });
    return response.data;
  },

  // Streaming version for analyze mode
  async analyzeRequirementsStream(request: GenerationRequest, onChunk: (chunk: { type: string; content?: string; diagram?: string; follow_up_questions?: string[]; error?: string }) => void) {
    try {
      console.log('Starting streaming analyze request to:', `${API_BASE_URL}/stream-analyze`);
      const response = await fetch(`${API_BASE_URL}/stream-analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          requirements: request.requirements,
        })
      });

      console.log('Streaming analyze response status:', response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let knowledgeContent = '';
      let diagramContent = '';
      let followUpQuestions: string[] = [];

      try {
        console.log('Starting to read streaming analyze response...');
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log('Streaming analyze completed');
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          
          // Process complete lines
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                console.log('Parsed streaming analyze data:', data);
                
                if (data.type === 'knowledge' && data.content) {
                  knowledgeContent += data.content;
                  onChunk({ type: 'knowledge', content: data.content });
                } else if (data.type === 'diagram' && data.diagram) {
                  diagramContent = data.diagram;
                  onChunk({ type: 'diagram', diagram: data.diagram });
                } else if (data.type === 'follow_up_questions' && data.follow_up_questions) {
                  followUpQuestions = data.follow_up_questions;
                  onChunk({ type: 'follow_up_questions', follow_up_questions: data.follow_up_questions });
                } else if (data.type === 'status') {
                  onChunk({ type: 'status', content: data.message });
                } else if (data.type === 'error' || data.error) {
                  console.error('Streaming analyze error received:', data.error);
                  onChunk({ type: 'error', error: data.error });
                } else if (data.type === 'done') {
                  console.log('Streaming analyze done signal received');
                  return {
                    knowledge_response: cleanResponseText(knowledgeContent),
                    architecture_diagram: diagramContent,
                    follow_up_questions: followUpQuestions,
                    mode: 'analysis',
                    success: true
                  };
                }
              } catch (e) {
                console.warn('Failed to parse streaming analyze data:', e, 'Line:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      return {
        knowledge_response: cleanResponseText(knowledgeContent),
        architecture_diagram: diagramContent,
        follow_up_questions: followUpQuestions,
        mode: 'analysis',
        success: true
      };
    } catch (error) {
      console.error('Streaming analyze error:', error);
      throw error;
    }
  },

  async generateArchitecture(request: GenerationRequest): Promise<GenerationResponse> {
    const response = await api.post('/generate', request);
    return response.data;
  },

  async handleFollowUpQuestion(question: string, architectureContext?: string, sessionId?: string) {
    const response = await api.post('/follow-up', {
      question,
      architecture_context: architectureContext,
    }, {
      params: sessionId ? { session_id: sessionId } : {}
    });
    return response.data;
  },

  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },
};
