import { useState, useEffect } from 'react';
import { apiService } from './services/api';
import { ChatMessage, ConversationContext, ConversationState, ActionButton } from './types';
import ChatInterface from './components/ChatInterface';
import ThemeToggle from './components/ThemeToggle';
import NebulaLogo from './components/NebulaLogo';
import EnhancedAnalysisDisplay from './components/EnhancedAnalysisDisplay';

function App() {
  console.log('App component rendering...');
  const [isDark, setIsDark] = useState(false);
  
  // Debug: Log when component mounts
  useEffect(() => {
    console.log('App component mounted successfully');
  }, []);
  
  const [conversationState, setConversationState] = useState<ConversationState>({
    messages: [],
    context: {
      mode: 'brainstorm',
      conversationHistory: []
    },
    isLoading: false
  });

  // Apply dark mode class to document
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  // Debug effect to monitor conversation state changes
  useEffect(() => {
    console.log('Conversation state changed:', {
      messageCount: conversationState.messages.length,
      isLoading: conversationState.isLoading,
      mode: conversationState.context.mode,
      hasLastResult: !!conversationState.context.lastResult
    });
  }, [conversationState]);

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date()
    };
    
    setConversationState(prev => ({
      ...prev,
      messages: [...prev.messages, newMessage]
    }));
  };

  const updateContext = (updates: Partial<ConversationContext>) => {
    setConversationState(prev => ({
      ...prev,
      context: { ...prev.context, ...updates }
    }));
  };

  const generateActionButtons = (_result: any, mode: string): ActionButton[] => {
    const actions: ActionButton[] = [];
    
    if (mode === 'brainstorm') {
      actions.push(
        { label: 'Analyze Requirements', action: 'analyze_requirements', icon: '🔍', color: 'green' },
        { label: 'Generate Architecture', action: 'generate_architecture', icon: '⚡', color: 'blue' }
      );
    } else if (mode === 'analyze') {
      actions.push(
        { label: 'Generate Architecture', action: 'generate_architecture', icon: '⚡', color: 'blue' },
        { label: 'Ask Questions', action: 'ask_questions', icon: '🧠', color: 'orange' }
      );
    } else if (mode === 'generate') {
      actions.push(
        { label: 'Modify Architecture', action: 'modify_architecture', icon: '✏️', color: 'blue' },
        { label: 'Explain Components', action: 'explain_components', icon: '📖', color: 'green' },
        { label: 'Cost Optimization', action: 'optimize_costs', icon: '💰', color: 'orange' }
      );
    }
    
    return actions;
  };

  const generateSuggestions = (_result: any, mode: string): string[] => {
    if (mode === 'brainstorm') {
      return [
        "Can you explain this in more detail?",
        "What are the alternatives?",
        "How does this compare to other AWS services?"
      ];
    } else if (mode === 'analyze') {
      return [
        "Can you make this more cost-effective?",
        "What about security considerations?",
        "How would this scale?"
      ];
    } else if (mode === 'generate') {
      return [
        "Add monitoring to this architecture",
        "Make this more secure",
        "Optimize for cost",
        "Add auto-scaling"
      ];
    }
    return [];
  };

  // Helper function to clean follow-up questions from content
  const cleanFollowUpQuestions = (text: string): string => {
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

  const handleSendMessage = async (message: string) => {
    // Add user message
    addMessage({
      type: 'user',
      content: message,
      mode: conversationState.context.mode
    });

    setConversationState(prev => ({ ...prev, isLoading: true }));

    try {
      const currentMode = conversationState.context.mode;
      
      // Check if this is a follow-up question about existing architecture
      const hasExistingArchitecture = conversationState.context.currentArchitecture;
      const isFollowUpQuestion = hasExistingArchitecture && 
        currentMode === 'generate' && 
        conversationState.context.conversationHistory.length > 0 &&
        conversationState.context.lastInteractionType === 'follow_up';

      if (isFollowUpQuestion) {
        // Handle as follow-up question using streaming brainstorming API
        try {
          // Add assistant message placeholder first
          addMessage({
            type: 'assistant',
            content: 'Thinking...',
            mode: currentMode,
            context: {}
          });
          
          // Use streaming brainstorming API for follow-up questions
          let streamingContent = '';
          let streamingResult: any = null;
          
          try {
            streamingResult = await apiService.brainstormKnowledgeStream(
              { requirements: message },
              (chunk: string) => {
                console.log('Received follow-up chunk:', chunk.substring(0, 50) + '...');
                streamingContent += chunk;
                // Update the assistant message with streaming content
                setConversationState(prev => {
                  const updatedMessages = [...prev.messages];
                  const lastMessage = updatedMessages[updatedMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'assistant') {
                    lastMessage.content = streamingContent;
                  }
                  return { ...prev, messages: updatedMessages };
                });
                
                // Remove the scroll trigger - ChatInterface handles it intelligently
                // The component will auto-scroll only if user is at bottom
              }
            );
            
            // Small delay to ensure streaming content is fully processed
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Update the final message with complete context for streaming result
            if (streamingResult && streamingResult.knowledge_response) {
              setConversationState(prev => {
                const updatedMessages = [...prev.messages];
                const lastMessage = updatedMessages[updatedMessages.length - 1];
                if (lastMessage && lastMessage.type === 'assistant') {
                  lastMessage.context = {
                    result: streamingResult,
                    suggestions: generateSuggestions(streamingResult, currentMode),
                    actions: generateActionButtons(streamingResult, currentMode),
                    follow_up_questions: (streamingResult as any).follow_up_questions || []
                  };
                }
                return { ...prev, messages: updatedMessages };
              });
              
              // Update context with streaming results
              updateContext({
                lastResult: streamingResult,
                conversationHistory: [...conversationState.context.conversationHistory, message],
                needsClarification: false,
                clarificationQuestions: [],
                lastInteractionType: 'follow_up'
              });
            }
            
            return; // Exit early for follow-up questions
          } catch (streamingError) {
            console.warn('Follow-up streaming failed, falling back to regular API:', streamingError);
            // Fallback to regular API call
            const result = await apiService.brainstormKnowledge({ requirements: message });
            
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = result.knowledge_response || 'Here\'s what I found about your question...';
                lastMessage.context = {
                  result: result,
                  suggestions: generateSuggestions(result, currentMode),
                  actions: generateActionButtons(result, currentMode),
                  follow_up_questions: (result as any).follow_up_questions || []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
            
            updateContext({
              lastResult: result,
              conversationHistory: [...conversationState.context.conversationHistory, message],
              needsClarification: false,
              clarificationQuestions: [],
              lastInteractionType: 'follow_up'
            });
            
            return; // Exit early for fallback
          }
        } catch (error) {
          console.error('Follow-up question failed:', error);
          addMessage({
            type: 'assistant',
            content: 'I encountered an error processing your follow-up question. Please try again.',
            mode: currentMode
          });
          return;
        }
      }

      // Original logic for initial requests
      if (currentMode === 'brainstorm') {
        console.log('Starting brainstorm mode with message:', message);
        
        // Add assistant message placeholder first
        addMessage({
          type: 'assistant',
          content: 'Thinking...',
          mode: currentMode,
          context: {}
        });
        
        try {
          // Try streaming first for better user experience (as per Strands Agents docs)
          console.log('Attempting streaming for better UX...');
          let streamingContent = '';
          let streamingResult: any = null;
          
          try {
            streamingResult = await apiService.brainstormKnowledgeStream(
              { requirements: message },
              (chunk: string) => {
                console.log('Received chunk:', chunk.substring(0, 50) + '...');
                streamingContent += chunk;
                // Clean the streaming content to remove follow-up questions from display
                const cleanedContent = cleanFollowUpQuestions(streamingContent);
                // Update the assistant message with cleaned streaming content
                setConversationState(prev => {
                  const updatedMessages = [...prev.messages];
                  const lastMessage = updatedMessages[updatedMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'assistant') {
                    lastMessage.content = cleanedContent;
                    console.log('Updated message content with streaming:', cleanedContent.substring(0, 100) + '...');
                  }
                  return { ...prev, messages: updatedMessages };
                });
                
                // Remove the scroll trigger - ChatInterface handles it intelligently
                // The component will auto-scroll only if user is at bottom
              }
            );
            console.log('Streaming completed successfully, result:', streamingResult);
            
            // Small delay to ensure streaming content is fully processed
            await new Promise(resolve => setTimeout(resolve, 100));
            
          } catch (streamingError) {
            console.warn('Streaming failed, falling back to regular API:', streamingError);
            // Fallback to regular API call
            const result = await apiService.brainstormKnowledge({ requirements: message });
            console.log('Brainstorm fallback result:', result);
            
            // Update the placeholder message with regular result
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = result.knowledge_response || 'Here\'s what I found about your question...';
                lastMessage.context = {
                  result: result,
                  suggestions: generateSuggestions(result, currentMode),
                  actions: generateActionButtons(result, currentMode),
                  follow_up_questions: (result as any).follow_up_questions || []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
            
            // Update context with results
            updateContext({
              lastResult: result,
              conversationHistory: [...conversationState.context.conversationHistory, message],
              needsClarification: false,
              clarificationQuestions: []
            });
            
            return; // Exit early for fallback
          }
          
          // Update the final message with complete context for streaming result
          if (streamingResult && streamingResult.knowledge_response) {
            console.log('Processing streaming result:', streamingResult);
            
            // Update the message with context
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                // Keep the existing content from streaming, just add context
                lastMessage.context = {
                  result: streamingResult,
                  suggestions: generateSuggestions(streamingResult, currentMode),
                  actions: generateActionButtons(streamingResult, currentMode),
                  follow_up_questions: (streamingResult as any).follow_up_questions || []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
            
            // Update context with streaming results
            updateContext({
              lastResult: streamingResult,
              conversationHistory: [...conversationState.context.conversationHistory, message],
              needsClarification: false,
              clarificationQuestions: []
            });
            
            console.log('Streaming result processed successfully');
          } else {
            console.warn('Invalid streaming result:', streamingResult);
            // Fallback to regular API if streaming result is invalid
            const result = await apiService.brainstormKnowledge({ requirements: message });
            console.log('Fallback result:', result);
            
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = result.knowledge_response || 'Here\'s what I found about your question...';
                lastMessage.context = {
                  result: result,
                  suggestions: generateSuggestions(result, currentMode),
                  actions: generateActionButtons(result, currentMode),
                  follow_up_questions: (result as any).follow_up_questions || []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
            
            updateContext({
              lastResult: result,
              conversationHistory: [...conversationState.context.conversationHistory, message],
              needsClarification: false,
              clarificationQuestions: []
            });
          }
          
          return; // Exit early for brainstorm mode
        } catch (error) {
          console.error('Brainstorm mode failed:', error);
          // Update the placeholder message with error
          setConversationState(prev => {
            const updatedMessages = [...prev.messages];
            const lastMessage = updatedMessages[updatedMessages.length - 1];
            if (lastMessage && lastMessage.type === 'assistant') {
              lastMessage.content = 'Sorry, I encountered an error processing your request. Please try again.';
            }
            return { ...prev, messages: updatedMessages };
          });
          return;
        }
      } else if (currentMode === 'analyze') {
        // Add assistant message placeholder first
        addMessage({
          type: 'assistant',
          content: 'Analyzing requirements...',
          mode: currentMode,
          context: {}
        });
        
        // Use streaming for analyze mode
        console.log('Attempting streaming for analyze mode...');
        let streamingContent = '';
        let streamingResult: any = null;
        let diagramContent = '';
        
        try {
          streamingResult = await apiService.analyzeRequirementsStream(
            { requirements: message },
            (chunk) => {
              if (chunk.type === 'knowledge' && chunk.content) {
                streamingContent += chunk.content;
                // Update the assistant message with streaming content
                setConversationState(prev => {
                  const updatedMessages = [...prev.messages];
                  const lastMessage = updatedMessages[updatedMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'assistant') {
                    // Create a new message object to ensure React detects the change
                    updatedMessages[updatedMessages.length - 1] = {
                      ...lastMessage,
                      content: streamingContent
                    };
                  }
                  return { ...prev, messages: updatedMessages };
                });
                
                // Remove the scroll trigger - ChatInterface handles it intelligently
                // The component will auto-scroll only if user is at bottom
              } else if (chunk.type === 'diagram' && chunk.diagram) {
                diagramContent = chunk.diagram;
                // Update message with diagram
                setConversationState(prev => {
                  const updatedMessages = [...prev.messages];
                  const lastMessage = updatedMessages[updatedMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'assistant') {
                    // Create a new message object with updated context
                    updatedMessages[updatedMessages.length - 1] = {
                      ...lastMessage,
                      context: {
                        ...lastMessage.context,
                        result: {
                          ...(lastMessage.context?.result || {}),
                          architecture_diagram: diagramContent
                        }
                      }
                    };
                  }
                  return { ...prev, messages: updatedMessages };
                });
              } else if (chunk.type === 'status' && chunk.content) {
                // Update status message
                setConversationState(prev => {
                  const updatedMessages = [...prev.messages];
                  const lastMessage = updatedMessages[updatedMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'assistant') {
                    lastMessage.content = streamingContent + '\n\n' + chunk.content;
                  }
                  return { ...prev, messages: updatedMessages };
                });
              } else if (chunk.type === 'error' && chunk.error) {
                console.error('Streaming error:', chunk.error);
                setConversationState(prev => {
                  const updatedMessages = [...prev.messages];
                  const lastMessage = updatedMessages[updatedMessages.length - 1];
                  if (lastMessage && lastMessage.type === 'assistant') {
                    lastMessage.content = streamingContent + '\n\nError: ' + chunk.error;
                  }
                  return { ...prev, messages: updatedMessages };
                });
              }
            }
          );
          
          console.log('Analyze streaming completed successfully, result:', streamingResult);
          
          // Small delay to ensure streaming content is fully processed
          await new Promise(resolve => setTimeout(resolve, 100));
          
        } catch (streamingError) {
          console.warn('Analyze streaming failed, falling back to regular API:', streamingError);
          try {
            // Fallback to regular API
            const result = await apiService.analyzeRequirements(message);
            streamingResult = result;
            streamingContent = result.knowledge_response || '';
            diagramContent = (result as any).architecture_diagram || '';
            const architectureExplanation = (result as any).architecture_explanation || '';
            
            // Update the message with fallback result
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = streamingContent || 'Analysis completed.';
                lastMessage.context = {
                  result: {
                    ...result,
                    knowledge_response: streamingContent,
                    architecture_diagram: diagramContent,
                    architecture_explanation: architectureExplanation
                  },
                  enhanced_analysis: result.enhanced_analysis,
                  suggestions: generateSuggestions(result, currentMode),
                  actions: generateActionButtons(result, currentMode),
                  follow_up_questions: (result as any).follow_up_questions || []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
          } catch (fallbackError) {
            console.error('Fallback API also failed:', fallbackError);
            // Update message with error
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = 'Sorry, I encountered an error processing your request. Please try again.';
              }
              return { ...prev, messages: updatedMessages };
            });
            return;
          }
        }
        
        // Update the final message with complete context
        if (streamingResult) {
          const finalContent = streamingContent || streamingResult.knowledge_response || 'Analysis completed.';
          
          setConversationState(prev => {
            const updatedMessages = [...prev.messages];
            const lastMessage = updatedMessages[updatedMessages.length - 1];
            if (lastMessage && lastMessage.type === 'assistant') {
              lastMessage.content = finalContent;
              lastMessage.context = {
                result: {
                  ...streamingResult,
                  knowledge_response: finalContent,
                  architecture_diagram: diagramContent || streamingResult.architecture_diagram,
                  architecture_explanation: (streamingResult as any).architecture_explanation || ''
                },
                enhanced_analysis: streamingResult.enhanced_analysis,
                suggestions: generateSuggestions(streamingResult, currentMode),
                actions: generateActionButtons(streamingResult, currentMode),
                follow_up_questions: streamingResult.follow_up_questions || []
              };
            }
            return { ...prev, messages: updatedMessages };
          });
          
          // Update context with results
          updateContext({
            lastResult: streamingResult,
            conversationHistory: [...conversationState.context.conversationHistory, message],
            needsClarification: false,
            clarificationQuestions: []
          });
        }
        
      } else {
        // Generate mode - use streaming
        console.log('Starting generate mode with message:', message);
        
        // Add assistant message placeholder first
        addMessage({
          type: 'assistant',
          content: 'Generating your architecture...',
          mode: currentMode,
          context: {}
        });
        
        try {
          // Try streaming first for better user experience
          console.log('Attempting streaming for generate mode...');
          let cloudformationContent = '';
          let diagramContent = '';
          let costEstimate: any = null;
          let streamingResult: any = null;
          let currentStatus = 'Generating your architecture...';
          
          try {
            streamingResult = await apiService.generateArchitectureStream(
              { requirements: message },
              (chunk: any) => {
                console.log('Received generate chunk:', chunk.type);
                
                if (chunk.type === 'status') {
                  // Update status message
                  currentStatus = chunk.content || chunk.message || 'Generating your architecture...';
                  setConversationState(prev => {
                    const updatedMessages = [...prev.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'assistant') {
                      lastMessage.content = currentStatus;
                    }
                    return { ...prev, messages: updatedMessages };
                  });
                } else if (chunk.type === 'cloudformation' && chunk.content) {
                  cloudformationContent += chunk.content;
                  // Stream the CloudFormation response in real-time
                  setConversationState(prev => {
                    const updatedMessages = [...prev.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'assistant') {
                      // Update message content with streaming CloudFormation response
                      lastMessage.content = `Generating CloudFormation template...\n\n${cloudformationContent}`;
                      // Store streaming response in context
                      if (!lastMessage.context) lastMessage.context = {};
                      if (!lastMessage.context.result) lastMessage.context.result = {};
                      lastMessage.context.result.cloudformation_response = cloudformationContent;
                    }
                    return { ...prev, messages: updatedMessages };
                  });
                } else if (chunk.type === 'cloudformation_complete' && (chunk.content || chunk.cloudformation)) {
                  cloudformationContent = chunk.content || chunk.cloudformation;
                  setConversationState(prev => {
                    const updatedMessages = [...prev.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'assistant') {
                      lastMessage.content = '✅ CloudFormation template generated\n\nGenerating architecture diagram...';
                      // Store full template in context for download/deploy
                      if (!lastMessage.context) lastMessage.context = {};
                      if (!lastMessage.context.result) lastMessage.context.result = {};
                      lastMessage.context.result.cloudformation_template = cloudformationContent;
                      // Store the full MCP server response
                      lastMessage.context.result.cloudformation_response = cloudformationContent;
                    }
                    return { ...prev, messages: updatedMessages };
                  });
                } else if (chunk.type === 'diagram' && chunk.content) {
                  diagramContent += chunk.content;
                } else if (chunk.type === 'diagram_complete' && chunk.diagram) {
                  diagramContent = chunk.diagram;
                  setConversationState(prev => {
                    const updatedMessages = [...prev.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'assistant') {
                      lastMessage.content = `✅ CloudFormation template generated\n✅ Architecture diagram generated\n\nGenerating cost estimate...`;
                      if (!lastMessage.context) lastMessage.context = {};
                      if (!lastMessage.context.result) lastMessage.context.result = {};
                      lastMessage.context.result.architecture_diagram = diagramContent;
                    }
                    return { ...prev, messages: updatedMessages };
                  });
                } else if (chunk.type === 'cost_complete' && chunk.cost_estimate) {
                  costEstimate = chunk.cost_estimate;
                  setConversationState(prev => {
                    const updatedMessages = [...prev.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    if (lastMessage && lastMessage.type === 'assistant') {
                      lastMessage.content = `I've generated your architecture with the following components:\n\n✅ CloudFormation template created\n✅ Architecture diagram generated\n✅ Cost estimate: ${costEstimate?.monthly_cost || '$500-1000'}`;
                      if (!lastMessage.context) lastMessage.context = {};
                      if (!lastMessage.context.result) lastMessage.context.result = {};
                      lastMessage.context.result.cost_estimate = costEstimate;
                    }
                    return { ...prev, messages: updatedMessages };
                  });
                }
                
                // Remove the scroll trigger - ChatInterface handles it intelligently
                // The component will auto-scroll only if user is at bottom
              }
            );
            
            // Update final message with complete results and context
            const responseContent = `I've generated your architecture with the following components:\n\n✅ CloudFormation template created\n✅ Architecture diagram generated\n✅ Cost estimate: ${streamingResult.cost_estimate?.monthly_cost || costEstimate?.monthly_cost || '$500-1000'}`;
            
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = responseContent;
                lastMessage.context = {
                  result: streamingResult,
                  suggestions: generateSuggestions(streamingResult, currentMode),
                  actions: generateActionButtons(streamingResult, currentMode),
                  follow_up_questions: []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
            
            // Update context with results
            updateContext({
              lastResult: streamingResult,
              conversationHistory: [...conversationState.context.conversationHistory, message],
              needsClarification: false,
              clarificationQuestions: []
            });
            
            // Update current architecture immediately
            if (streamingResult.cloudformation_template) {
              updateContext({
                currentArchitecture: {
                  cloudformation: streamingResult.cloudformation_template,
                  diagram: streamingResult.architecture_diagram,
                  cost: streamingResult.cost_estimate
                }
              });
            }
            
          } catch (streamingError) {
            console.warn('Generate streaming failed, falling back to regular API:', streamingError);
            // Fallback to regular API call
            const result = await apiService.generateArchitecture({ requirements: message });
            
            const responseContent = `I've generated your architecture with the following components:\n\n✅ CloudFormation template created\n✅ Architecture diagram generated\n✅ Cost estimate: ${result.cost_estimate?.monthly_cost || '$500-1000'}`;
            
            setConversationState(prev => {
              const updatedMessages = [...prev.messages];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              if (lastMessage && lastMessage.type === 'assistant') {
                lastMessage.content = responseContent;
                lastMessage.context = {
                  result: {
                    cloudformation_template: result.cloudformation_template,
                    architecture_diagram: result.architecture_diagram,
                    cost_estimate: result.cost_estimate
                  },
                  suggestions: generateSuggestions(result, currentMode),
                  actions: generateActionButtons(result, currentMode),
                  follow_up_questions: []
                };
              }
              return { ...prev, messages: updatedMessages };
            });
            
            updateContext({
              lastResult: result,
              conversationHistory: [...conversationState.context.conversationHistory, message],
              needsClarification: false,
              clarificationQuestions: []
            });
            
            if (result.cloudformation_template) {
              updateContext({
                currentArchitecture: {
                  cloudformation: result.cloudformation_template,
                  diagram: result.architecture_diagram,
                  cost: result.cost_estimate
                }
              });
            }
          }
        } catch (error) {
          console.error('Generate mode failed:', error);
          addMessage({
            type: 'assistant',
            content: 'I encountered an error generating your architecture. Please try again.',
            mode: currentMode
          });
        }
      }

    } catch (error) {
      console.error('Failed to process message:', error);
      console.error('Error details:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      // Add error message to chat
      addMessage({
        type: 'assistant',
        content: `Sorry, I encountered an error processing your request: ${errorMessage}. Please try again.`,
        mode: conversationState.context.mode
      });
      
      // Show error in console for debugging
      console.error('Full error object:', error);
    } finally {
      setConversationState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleActionClick = async (action: string) => {
    
    switch (action) {
      case 'analyze_requirements':
        updateContext({ mode: 'analyze' });
        addMessage({
          type: 'assistant',
          content: 'Switched to analysis mode. Please describe your requirements and I\'ll analyze which AWS services you need.',
          mode: 'analyze'
        });
        break;
        
      case 'generate_architecture':
        updateContext({ mode: 'generate' });
        addMessage({
          type: 'assistant',
          content: 'Switched to generation mode. Please describe your architecture needs and I\'ll generate CloudFormation templates, diagrams, and cost estimates.',
          mode: 'generate'
        });
        break;
        
      case 'modify_architecture':
        // Handle architecture modification with context
        if (conversationState.context.currentArchitecture) {
          const architectureContext = JSON.stringify(conversationState.context.currentArchitecture);
          try {
            const result = await apiService.handleFollowUpQuestion(
              'What modifications can I make to this architecture? Please suggest specific changes and improvements.',
              architectureContext,
              conversationState.context.sessionId
            );
            addMessage({
              type: 'assistant',
              content: result.answer,
              mode: 'generate',
              context: {
                result,
                response_type: 'follow_up_answer'
              }
            });
          } catch (error) {
            addMessage({
              type: 'assistant',
              content: 'I can help you modify the current architecture. What specific changes would you like to make?',
              mode: 'generate'
            });
          }
        } else {
          addMessage({
            type: 'assistant',
            content: 'Please generate an architecture first, then I can help you modify it.',
            mode: 'generate'
          });
        }
        break;
        
      case 'explain_components':
        // Handle component explanation with context
        if (conversationState.context.currentArchitecture) {
          const architectureContext = JSON.stringify(conversationState.context.currentArchitecture);
          try {
            const result = await apiService.handleFollowUpQuestion(
              'Please explain the components in this architecture. What does each service do and how do they work together?',
              architectureContext,
              conversationState.context.sessionId
            );
            addMessage({
              type: 'assistant',
              content: result.answer,
              mode: 'generate',
              context: {
                result,
                response_type: 'follow_up_answer'
              }
            });
          } catch (error) {
            addMessage({
              type: 'assistant',
              content: 'I can explain the components in your architecture. Which specific component would you like me to explain?',
              mode: 'generate'
            });
          }
        } else {
          addMessage({
            type: 'assistant',
            content: 'Please generate an architecture first, then I can explain the components.',
            mode: 'generate'
          });
        }
        break;
        
      case 'optimize_costs':
        // Handle cost optimization with context
        if (conversationState.context.currentArchitecture) {
          const architectureContext = JSON.stringify(conversationState.context.currentArchitecture);
          try {
            const result = await apiService.handleFollowUpQuestion(
              'How can I optimize this architecture for cost? Please suggest specific cost-saving strategies and alternatives.',
              architectureContext,
              conversationState.context.sessionId
            );
            addMessage({
              type: 'assistant',
              content: result.answer,
              mode: 'generate',
              context: {
                result,
                response_type: 'follow_up_answer'
              }
            });
          } catch (error) {
            addMessage({
              type: 'assistant',
              content: 'I can help optimize your architecture for cost. What specific cost concerns do you have?',
              mode: 'generate'
            });
          }
        } else {
          addMessage({
            type: 'assistant',
            content: 'Please generate an architecture first, then I can help optimize it for cost.',
            mode: 'generate'
          });
        }
        break;
        
      default:
        // Handle other actions or pass them as messages
        await handleSendMessage(action);
    }
  };

  return (
    <div className="h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
      {/* Modern Compact Header */}
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-soft">
        <div className="max-w-full px-6 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <NebulaLogo size="md" showText={true} />
              <div className="hidden lg:flex items-center">
                <span className="text-gray-300 dark:text-gray-700 mx-3">|</span>
                <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                  Intelligent AI Co-Architect for your cloud journey
                </p>
              </div>
            </div>
            <ThemeToggle isDark={isDark} onToggle={toggleTheme} />
          </div>
        </div>
      </header>

      {/* Main Content - Single Column Layout */}
      <main className="flex-1 flex overflow-hidden">
        <div className="w-full overflow-hidden">
          <ChatInterface
            messages={conversationState.messages}
            context={conversationState.context}
            isLoading={conversationState.isLoading}
            onSendMessage={handleSendMessage}
            onActionClick={handleActionClick}
            onModeChange={(mode) => updateContext({ mode })}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
