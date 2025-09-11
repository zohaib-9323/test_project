/**
 * Company Dashboard Page
 *
 * This page provides company users with:
 * - Company profile management
 * - Job posting creation and management
 * - Application tracking
 * - Company statistics
 *
 * Only users with 'company' or 'admin' role can access this page.
 */

'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import {
  jobAPI,
  Company,
  JobWithCompany,
  CompanyCreate,
  JobCreate,
} from '@/lib/api';
import {
  Building2,
  Plus,
  Briefcase,
  Users,
  Edit3,
  Trash2,
  Eye,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import toast from 'react-hot-toast';
import EmailVerificationGuard from '@/components/EmailVerificationGuard';

export default function CompanyDashboard() {
  const { user, loading } = useAuth();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [jobs, setJobs] = useState<JobWithCompany[]>([]);
  const [loadingData, setLoadingData] = useState(false);
  const [_showCreateCompany, _setShowCreateCompany] = useState(false);
  const [_showCreateJob, _setShowCreateJob] = useState(false);
  const [_selectedCompany, _setSelectedCompany] = useState<Company | null>(
    null
  );

  // Check if user has company access
  const hasCompanyAccess = user?.role === 'company' || user?.role === 'admin';

  useEffect(() => {
    if (hasCompanyAccess) {
      loadCompanyData();
    }
  }, [hasCompanyAccess]);

  const loadCompanyData = async () => {
    try {
      setLoadingData(true);

      // Load companies
      const companiesResponse = await jobAPI.getCompanies(1, 100);
      setCompanies(companiesResponse.data.companies);

      // Load jobs
      const jobsResponse = await jobAPI.getJobs({ page: 1, per_page: 50 });
      setJobs(jobsResponse.data.jobs);
    } catch (error: unknown) {
      console.error('Failed to load company data:', error);
      toast.error('Failed to load company data');
    } finally {
      setLoadingData(false);
    }
  };

  const _handleCreateCompany = async (companyData: CompanyCreate) => {
    try {
      await jobAPI.createCompany(companyData);
      toast.success('Company created successfully!');
      _setShowCreateCompany(false);
      loadCompanyData();
    } catch (error: unknown) {
      console.error('Failed to create company:', error);
      toast.error('Failed to create company');
    }
  };

  const _handleCreateJob = async (jobData: JobCreate) => {
    try {
      await jobAPI.createJob(jobData);
      toast.success('Job posted successfully!');
      _setShowCreateJob(false);
      loadCompanyData();
    } catch (error: unknown) {
      console.error('Failed to create job:', error);
      toast.error('Failed to create job');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="text-gray-600">Loading...</span>
        </div>
      </div>
    );
  }

  if (!hasCompanyAccess) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Access Denied
          </h2>
          <p className="text-gray-600">
            Only company users and admins can access this page.
          </p>
        </div>
      </div>
    );
  }

  return (
    <EmailVerificationGuard>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Company Dashboard
            </h1>
            <p className="text-gray-600">
              Manage your companies and job postings
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Building2 className="h-6 w-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Companies</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {companies.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Briefcase className="h-6 w-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Active Jobs
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {jobs.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Users className="h-6 w-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Applications
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">0</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 mb-8">
            <button
              onClick={() => _setShowCreateCompany(true)}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Create Company</span>
            </button>

            <button
              onClick={() => _setShowCreateJob(true)}
              className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Post Job</span>
            </button>
          </div>

          {/* Companies Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Your Companies
              </h2>
            </div>

            {loadingData ? (
              <div className="p-6 text-center">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">Loading companies...</p>
              </div>
            ) : companies.length === 0 ? (
              <div className="p-6 text-center">
                <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No companies yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Create your first company to start posting jobs.
                </p>
                <button
                  onClick={() => _setShowCreateCompany(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Create Company
                </button>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {companies.map(company => (
                  <div key={company.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {company.name}
                        </h3>
                        {company.description && (
                          <p className="text-gray-600 mt-1">
                            {company.description}
                          </p>
                        )}
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          {company.industry && (
                            <span>Industry: {company.industry}</span>
                          )}
                          {company.size && <span>Size: {company.size}</span>}
                          {company.location && (
                            <span>Location: {company.location}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-600 transition-colors">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Jobs Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Your Job Postings
              </h2>
            </div>

            {loadingData ? (
              <div className="p-6 text-center">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">Loading jobs...</p>
              </div>
            ) : jobs.length === 0 ? (
              <div className="p-6 text-center">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No jobs posted yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Create your first job posting to attract candidates.
                </p>
                <button
                  onClick={() => _setShowCreateJob(true)}
                  className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Post Job
                </button>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {jobs.map(job => (
                  <div key={job.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {job.title}
                        </h3>
                        <p className="text-gray-600 mt-1">{job.company.name}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span>{job.employment_type.replace('-', ' ')}</span>
                          <span>{job.experience_level} level</span>
                          {job.location && <span>{job.location}</span>}
                          {job.remote_work && (
                            <span className="text-blue-600">Remote OK</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                          <Eye className="h-4 w-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-600 transition-colors">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </EmailVerificationGuard>
  );
}
