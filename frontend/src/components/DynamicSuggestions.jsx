import React, { useState, useEffect } from 'react';
import { Sparkles, School, Globe, ShoppingBag, BookOpen, TestTube, Calculator, Search } from 'lucide-react';

const DynamicSuggestions = ({ selectedModel, onSuggestionClick }) => {
  const [currentSuggestions, setCurrentSuggestions] = useState([]);
  const [animatingIndices, setAnimatingIndices] = useState(new Set());

  const suggestions = {
    general: [
      { text: "Help me understand photosynthesis", icon: TestTube },
      { text: "Explain the Pythagorean theorem", icon: Calculator },
      { text: "What are effective study techniques?", icon: BookOpen },
      { text: "How to write a research paper?", icon: BookOpen },
      { text: "Explain Newton's laws of motion", icon: TestTube },
      { text: "Best note-taking methods for students", icon: BookOpen },
      { text: "How to prepare for exams effectively?", icon: School },
      { text: "Explain the water cycle", icon: Globe },
      { text: "Help with essay structure", icon: BookOpen },
      { text: "What is the scientific method?", icon: TestTube },
      { text: "How to solve quadratic equations?", icon: Calculator },
      { text: "Explain cellular respiration", icon: TestTube },
      { text: "Tips for academic writing", icon: BookOpen },
      { text: "How to manage homework effectively?", icon: School },
      { text: "Explain the periodic table", icon: TestTube },
      { text: "Help with time management for students", icon: School },
      { text: "What are literary devices?", icon: BookOpen },
      { text: "How to improve reading comprehension?", icon: BookOpen }
    ],
    everest: [
      { text: "Study guide for Grade 9 Unit 2 Science", icon: School },
      { text: "Practice test for Grade 9 Mathematics", icon: Calculator },
      { text: "Explain photosynthesis for Grade 9", icon: TestTube },
      { text: "Grade 9 Physics: Laws of Motion", icon: School },
      { text: "Chemistry basics for Grade 9 students", icon: TestTube },
      { text: "Grade 9 English literature analysis", icon: BookOpen },
      { text: "Math problems for Grade 9 algebra", icon: Calculator },
      { text: "Science project ideas for Grade 9", icon: TestTube },
      { text: "Grade 9 history timeline summary", icon: BookOpen },
      { text: "Biology cell structure for Grade 9", icon: School },
      { text: "Grade 9 Geography: Climate zones", icon: Globe },
      { text: "Trigonometry basics for Grade 9", icon: Calculator },
      { text: "Grade 9 Chemistry: Periodic table", icon: TestTube },
      { text: "Essay writing tips for Grade 9", icon: BookOpen },
      { text: "Grade 9 Physics experiments", icon: TestTube },
      { text: "Exam preparation for Grade 9 finals", icon: School },
      { text: "Grade 9 Computer Science basics", icon: Calculator },
      { text: "Study schedule for Grade 9 students", icon: School }
    ],
    'web-scraper': [
      { text: "Research Khan Academy for calculus tutorials", icon: BookOpen },
      { text: "Find MIT OpenCourseWare lectures on physics", icon: School },
      { text: "Search Google Scholar for research papers", icon: Search },
      { text: "Check Coursera for academic courses", icon: BookOpen },
      { text: "Browse Wikipedia for historical events", icon: Globe },
      { text: "Find educational videos on YouTube", icon: Search },
      { text: "Search JSTOR for academic journals", icon: BookOpen },
      { text: "Check university websites for admission requirements", icon: School },
      { text: "Find free textbooks on OpenStax", icon: BookOpen },
      { text: "Research scientific articles on Nature.com", icon: TestTube },
      { text: "Browse educational resources on edX", icon: School },
      { text: "Search for scholarship opportunities", icon: Search },
      { text: "Find academic conferences in your field", icon: Globe },
      { text: "Check university library databases", icon: BookOpen },
      { text: "Research citation formats on Purdue OWL", icon: BookOpen },
      { text: "Find online tutoring resources", icon: School },
      { text: "Search for academic competitions", icon: Globe },
      { text: "Browse educational apps for students", icon: Search },
      { text: "Find study groups and forums", icon: School },
      { text: "Research graduate school programs", icon: Globe }
    ]
  };

  // Initialize suggestions
  useEffect(() => {
    const modelSuggestions = suggestions[selectedModel] || suggestions.general;
    const shuffled = [...modelSuggestions].sort(() => Math.random() - 0.5);
    setCurrentSuggestions(shuffled.slice(0, 3));
  }, [selectedModel]);

  // Cycle suggestions
  useEffect(() => {
    const interval = setInterval(() => {
      const modelSuggestions = suggestions[selectedModel] || suggestions.general;
      const randomIndex = Math.floor(Math.random() * 3);
      
      setAnimatingIndices(new Set([randomIndex]));
      
      setTimeout(() => {
        setCurrentSuggestions(prev => {
          const newSuggestions = [...prev];
          const availableSuggestions = modelSuggestions.filter(
            s => !prev.some(p => p.text === s.text)
          );
          
          if (availableSuggestions.length > 0) {
            const randomSuggestion = availableSuggestions[
              Math.floor(Math.random() * availableSuggestions.length)
            ];
            newSuggestions[randomIndex] = randomSuggestion;
          }
          
          return newSuggestions;
        });
        
        setTimeout(() => {
          setAnimatingIndices(new Set());
        }, 300);
      }, 300);
    }, 2500); // Change every 2.5 seconds

    return () => clearInterval(interval);
  }, [selectedModel]);

  const getCategoryIcon = () => {
    switch(selectedModel) {
      case 'everest':
        return <School className="w-4 h-4" />;
      case 'web-scraper':
        return <Globe className="w-4 h-4" />;
      default:
        return <Sparkles className="w-4 h-4" />;
    }
  };

  const getCategoryColor = () => {
    switch(selectedModel) {
      case 'everest':
        return 'from-yellow-600 to-yellow-500';
      case 'web-scraper':
        return 'from-blue-900 to-blue-800';
      default:
        return 'from-blue-900 to-yellow-600';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mb-4">
      <div className="flex items-center gap-2 mb-3 text-sm text-gray-600 dark:text-gray-400">
        <div className={`bg-gradient-to-r ${getCategoryColor()} p-1 rounded`}>
          {React.cloneElement(getCategoryIcon(), { className: "w-3.5 h-3.5 text-white" })}
        </div>
        <span className="font-medium">Academic inquiries:</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {currentSuggestions.map((suggestion, index) => {
          const Icon = suggestion.icon;
          const isAnimating = animatingIndices.has(index);
          
          return (
            <button
              key={`${selectedModel}-${index}`}
              onClick={() => onSuggestionClick(suggestion.text)}
              className={`
                group relative overflow-hidden rounded-lg p-3 text-left
                bg-gradient-to-r ${getCategoryColor()} bg-opacity-5
                border border-gray-200 dark:border-gray-700
                hover:border-gray-300 dark:hover:border-gray-600
                transition-all duration-300 transform
                ${isAnimating ? 'scale-95 opacity-0' : 'scale-100 opacity-100'}
                hover:scale-[1.02] hover:shadow-md
              `}
              style={{
                transition: 'all 0.3s ease-in-out',
              }}
            >
              <div className="flex items-start gap-3">
                <div className={`
                  p-1.5 rounded-md bg-gradient-to-r ${getCategoryColor()}
                  text-white opacity-80 group-hover:opacity-100
                  transition-opacity duration-200
                `}>
                  <Icon className="w-4 h-4" />
                </div>
                
                <span className="text-sm text-gray-700 dark:text-gray-300 
                  group-hover:text-gray-900 dark:group-hover:text-gray-100
                  line-clamp-2 transition-colors duration-200">
                  {suggestion.text}
                </span>
              </div>
              
              {/* Hover effect */}
              <div className={`
                absolute inset-0 bg-gradient-to-r ${getCategoryColor()} 
                opacity-0 group-hover:opacity-10 transition-opacity duration-300
              `} />
              
              {/* Shimmer effect */}
              <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full 
                transition-transform duration-700 ease-in-out">
                <div className="h-full w-12 bg-gradient-to-r from-transparent 
                  via-white/20 to-transparent skew-x-12" />
              </div>
            </button>
          );
        })}
      </div>
      
      {/* Dots indicator */}
      <div className="flex justify-center gap-1 mt-4">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={`
              h-1 rounded-full transition-all duration-300
              ${animatingIndices.has(i) 
                ? 'w-6 bg-gradient-to-r ' + getCategoryColor()
                : 'w-1 bg-gray-300 dark:bg-gray-600'
              }
            `}
          />
        ))}
      </div>
    </div>
  );
};

export default DynamicSuggestions;