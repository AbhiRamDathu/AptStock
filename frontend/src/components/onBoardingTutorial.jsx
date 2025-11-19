import React from 'react';

const OnboardingTour = ({ isOpen, onClose, currentStep, setCurrentStep }) => {
  const steps = [
    {
      target: '#upload-zone',
      title: '📊 Step 1: Upload Your Sales Data',
      content: 'Drag and drop your CSV file here or click to browse. Make sure your file has columns: date, sku, store, units_sold.',
      position: 'bottom'
    },
    {
      target: '#config-section',
      title: '⚙️ Step 2: Configure Your Analysis',
      content: 'Select your store and set the date range for analysis. This determines the historical data used for AI training.',
      position: 'top'
    },
    {
      target: '#upload-button',
      title: '🚀 Step 3: Generate AI Forecast',
      content: 'Click to upload your data and train Prophet AI models. Our system will automatically detect patterns and generate forecasts.',
      position: 'top'
    },
    {
      target: '#charts-section',
      title: '📈 Step 4: Analyze Your Results',
      content: 'View interactive charts comparing historical sales with AI predictions. Confidence bands show prediction uncertainty.',
      position: 'top'
    },
    {
      target: '#alerts-section',
      title: '⚠️ Step 5: Monitor Stock Alerts',
      content: 'Get automatic alerts for low/high demand forecasts to optimize your inventory levels.',
      position: 'top'
    },
    {
      target: '#recommendations-section',
      title: '💡 Step 6: Apply Recommendations',
      content: 'Review AI-generated reorder points and safety stock recommendations to improve your inventory management.',
      position: 'top'
    }
  ];

  const currentStepData = steps[currentStep];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onClose();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800">Welcome to APDF! 🎉</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        </div>

        <div className="mb-6">
          <div className="flex items-center mb-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold mr-3">
              {currentStep + 1}
            </div>
            <h4 className="font-semibold text-lg">{currentStepData.title}</h4>
          </div>
          <p className="text-gray-600 leading-relaxed">{currentStepData.content}</p>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex space-x-1">
            {steps.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentStep ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          <div className="flex space-x-3">
            {currentStep > 0 && (
              <button
                onClick={prevStep}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Previous
              </button>
            )}
            <button
              onClick={nextStep}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {currentStep === steps.length - 1 ? 'Get Started!' : 'Next'}
            </button>
          </div>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Step {currentStep + 1} of {steps.length}
          </p>
        </div>
      </div>
    </div>
  );
};

export default OnboardingTour;
