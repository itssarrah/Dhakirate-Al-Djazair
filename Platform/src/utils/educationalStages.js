import stagesData from './EducationalStage.json';

export const getEducationalStages = () => {
    try {
        return stagesData.educationalStages.map(stage => ({
            code: stage.Level,
            name: stage.Name,
            hasExtendedQuizzes: stage['HasQuiz2&3']
        }));
    } catch (error) {
        console.error('Error processing educational stages:', error);
        return [];
    }
};

// Optional: Add helper function to get stage info by code
export const getStageByCode = (code) => {
    try {
        const stage = stagesData.educationalStages.find(s => s.Level === code);
        return stage ? {
            code: stage.Level,
            name: stage.Name,
            hasExtendedQuizzes: stage['HasQuiz2&3']
        } : null;
    } catch (error) {
        console.error('Error getting stage by code:', error);
        return null;
    }
};

export const getNextStage = (currentStage) => {
    const stageMapping = {
        'PS1': 'PS2', 'PS2': 'PS3', 'PS3': 'PS4', 'PS4': 'PS5', 'PS5': 'JS1',
        'JS1': 'JS2', 'JS2': 'JS3', 'JS3': 'JS4', 'JS4': ['HSS1', 'HSL1'],
        'HSS1': 'HSS2', 'HSS2': 'HSS3',
        'HSL1': 'HSL2', 'HSL2': 'HSL3',
        'HSS3': 'UNI', 'HSL3': 'UNI'
    };
    return stageMapping[currentStage] || null;
};

export const isHighSchoolChoice = (currentStage) => {
    return currentStage === 'JS4';
};

export const getStageNameForDisplay = (stageCode) => {
    const stage = getStageByCode(stageCode);
    return stage ? stage.name : '';
};
