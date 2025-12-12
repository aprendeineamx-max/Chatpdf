
import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { Brain, Star, Code, Zap } from 'lucide-react';

interface AgentSkill {
    id: string;
    name: string;
    category: string;
    proficiency: number;
}

export function SkillGalaxy() {
    const [skills, setSkills] = useState<AgentSkill[]>([]);

    useEffect(() => {
        fetchSkills();
    }, []);

    async function fetchSkills() {
        const { data } = await supabase.from('agent_skills').select('*').order('proficiency', { ascending: false });
        if (data) setSkills(data);
    }

    // Group by category
    const categories: Record<string, AgentSkill[]> = {
        'Language': [],
        'Framework': [],
        'Tool': []
    };

    skills.forEach(s => {
        if (!categories[s.category]) categories[s.category] = [];
        categories[s.category].push(s);
    });

    return (
        <div className="flex-1 bg-[#0f0f13] p-8 overflow-y-auto">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent mb-6 flex items-center gap-2">
                <Brain className="w-8 h-8 text-purple-400" />
                Meta-Learning: Skill Galaxy
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {Object.entries(categories).map(([category, items]) => (
                    <div key={category} className="space-y-4">
                        <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest border-b border-gray-800 pb-2">
                            {category} Intelligence
                        </h3>
                        {items.map(skill => (
                            <div key={skill.id} className="relative group">
                                <div className="bg-[#1a1a20] border border-gray-800 rounded-lg p-4 hover:border-purple-500/50 transition-all">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-mono font-bold text-white">{skill.name}</span>
                                        <div className="flex gap-0.5">
                                            {[...Array(5)].map((_, i) => (
                                                <div
                                                    key={i}
                                                    className={`w-1 h-3 rounded-full ${(i + 1) * 10 <= skill.proficiency ? 'bg-purple-500' : 'bg-gray-800'
                                                        }`}
                                                />
                                            ))}
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                            style={{ width: `${skill.proficiency}%` }}
                                        />
                                    </div>
                                    <div className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                                        <Zap className="w-3 h-3 text-yellow-500" />
                                        Proficiency Level: {skill.proficiency}/100
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
}
