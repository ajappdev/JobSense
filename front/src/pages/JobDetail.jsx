import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { ArrowLeft, ExternalLink, Trash2, EyeOffIcon } from 'lucide-react';

const mockJob = {
  id: 1,
  title: 'Senior React Developer',
  company: 'TechCorp',
  location: 'San Francisco, CA',
  salary: '$140k–$180k',
  description: `
    <p>We are looking for a Senior React Developer to join our team...</p>
    <h3>Responsibilities:</h3>
    <ul>
      <li>Build scalable web applications</li>
      <li>Mentor junior developers</li>
      <li>Write clean, maintainable code</li>
    </ul>
    <h3>Requirements:</h3>
    <ul>
      <li>5+ years React experience</li>
      <li>Expert in TypeScript</li>
      <li>Experience with Next.js</li>
    </ul>
  `,
  url: 'https://example.com/job/123',
  match: 85,
  skills: ['React', 'TypeScript', 'Next.js']
};

export default function JobDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);

  useEffect(() => {
    // API placeholder
    fetch(`/api/jobs/${id}`)
      .then(res => res.json())
      .then(data => setJob(data))
      .catch(() => setJob(mockJob)); // fallback
  }, [id]);

  const ignoreJob = () => {
    fetch(`/api/jobs/${id}/ignore`, { method: 'POST' });
    navigate('/jobs');
  };

  if (!job) return <div className="p-6 text-center text-slate-400">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition-colors cursor-pointer mb-6"
      >
        <ArrowLeft className="w-5 h-5" /> Back to Jobs
      </button>

      <div className="bg-slate-800 rounded-lg shadow-xl border border-slate-700 p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">{job.title}</h1>
            <p className="text-lg text-slate-300">{job.company} • {job.location}</p>
            {job.salary && <p className="text-green-400 font-medium">{job.salary}</p>}
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-green-400">{job.match}%</p>
            <p className="text-sm text-slate-400">Skill Match</p>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="font-semibold mb-2 text-white">Required Skills</h3>
          <div className="flex flex-wrap gap-2">
            {job.skills.map(skill => (
              <span key={skill} className="px-3 py-1 bg-blue-900 text-blue-100 rounded-full text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div 
          className="prose prose-invert max-w-none mb-6 text-slate-300"
          dangerouslySetInnerHTML={{ __html: job.description }}
        />

        <div className="flex gap-3 justify-end">

          <button
            onClick={ignoreJob}
            className="flex items-center gap-2 border border-slate-600 text-slate-400 px-4 py-2 rounded-md hover:bg-slate-700 transition-all cursor-pointer"
          >
            <EyeOffIcon className="w-5 h-5" /> Ignore
          </button>

          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors cursor-pointer"
          >
            <ExternalLink className="w-5 h-5" /> Apply on Original Site
          </a>

        </div>
      </div>
    </div>
  );
}