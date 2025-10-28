import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ExternalLink, EyeOffIcon } from 'lucide-react';

export default function Jobs() {

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Example job board link (replace with real from Settings later)
  const JOB_BOARD_LINK = 'https://example.com/jobs';

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch('http://localhost:5001/get-jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ link: JOB_BOARD_LINK })
        });

        const data = await response.json();

        if (data.success) {
          setJobs(data.jobs.map((job, i) => ({
            id: job.job_link || i,
            title: job.title || 'Untitled Job',
            match: job.match_score || Math.floor(Math.random() * 40) + 60, // fallback
            skills: job.skills || [],
            company: job.company || 'Unknown',
            url: job.job_link
          })));
        } else {
          setError(data.error || 'Failed to fetch jobs');
        }
      } catch (err) {
        setError('Network error. Is the server running?');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);


  const ignoreJob = (id) => {
    // API placeholder
    fetch(`/api/jobs/${id}/ignore`, { method: 'POST' });
  };

  if (loading) return <div className="p-6 text-center">Loading jobs...</div>;
  if (error) return <div className="p-6 text-center text-red-600">{error}</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-white">Aggregated Jobs</h1>
      
      <div className="bg-slate-800 rounded-lg shadow-xl border border-slate-700 overflow-hidden">
        <table className="min-w-full divide-y divide-slate-700">
          <thead className="bg-slate-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Title</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Match</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Skills</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Company</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider"></th>
            </tr>
          </thead>
          <tbody className="bg-slate-800 divide-y divide-slate-700">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-slate-400">
                  No jobs yet. Add job boards in Settings.
                </td>
              </tr>
            ) : (
              jobs.map(job => (
                <tr key={job.id} className="hover:bg-slate-700 transition-colors">
                  <td onClick={() => navigate(`/jobs/${job.id}`)} className="px-6 py-4 whitespace-nowrap font-medium text-white cursor-pointer">
                    {job.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-300">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      <span>{job.match}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {job.skills.map(skill => (
                        <span key={skill} className="px-2 py-1 bg-blue-900 text-blue-100 text-xs rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-300">
                    {job.company}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <div className="flex gap-3 justify-end">
                        <button
                        onClick={() => ignoreJob(job.id)}
                        className="text-slate-400 hover:text-slate-300 transition-colors cursor-pointer"
                        title="Ignore"
                        >
                        <EyeOffIcon className="w-5 h-5" />
                        </button>
                        <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="Apply"
                            className="text-slate-400 hover:text-slate-300 transition-colors cursor-pointer"
                        >
                            <ExternalLink className="w-5 h-5" />
                        </a>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}