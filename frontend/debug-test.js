// Simple test to debug the brainstorm issue
const testBrainstorm = async () => {
  try {
    console.log('Testing brainstorm API...');
    const response = await fetch('http://localhost:8000/brainstorm', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ requirements: 'What is AWS Lambda?' })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Brainstorm response:', data);
    return data;
  } catch (error) {
    console.error('Brainstorm test error:', error);
    throw error;
  }
};

// Run the test
testBrainstorm();
