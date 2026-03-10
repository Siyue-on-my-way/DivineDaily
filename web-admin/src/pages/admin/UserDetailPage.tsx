import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getUserDetail, getUserDivinations } from '../../api/user';
import { UserDetail, UserDivination } from '../../types/user';
import { useToast } from '../../hooks/useToast';
import UserInfoCard from '../../components/user/UserInfoCard';
import DivinationStatsCard from '../../components/user/DivinationStatsCard';
import DivinationHistoryList from '../../components/user/DivinationHistoryList';
import DivinationDetailModal from '../../components/user/DivinationDetailModal';
import './UserDetailPage.css';

export default function UserDetailPage() {
  const { userId } = useParams<{ userId: string }>();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [user, setUser] = useState<UserDetail | null>(null);
  const [divinations, setDivinations] = useState<UserDivination[]>([]);
  const [loading, setLoading] = useState(true);
  const [divinationLoading, setDivinationLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [selectedDivination, setSelectedDivination] = useState<UserDivination | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 加载用户详情
  useEffect(() => {
    if (!userId) return;
    
    const loadUserDetail = async () => {
      setLoading(true);
      try {
        const data = await getUserDetail(parseInt(userId));
        setUser(data);
      } catch (error: any) {
        showToast(error.response?.data?.detail || '加载用户详情失败', 'error');
        navigate('/admin/users');
      } finally {
        setLoading(false);
      }
    };

    loadUserDetail();
  }, [userId]);

  // 加载占卜历史
  useEffect(() => {
    if (!userId) return;
    
    const loadDivinations = async () => {
      setDivinationLoading(true);
      try {
        const data = await getUserDivinations(
          parseInt(userId), 
          currentPage, 
          10,
          filterType,
          searchKeyword
        );
        setDivinations(data.divinations);
        setTotal(data.total);
      } catch (error: any) {
        showToast(error.response?.data?.detail || '加载占卜历史失败', 'error');
      } finally {
        setDivinationLoading(false);
      }
    };

    loadDivinations();
  }, [userId, currentPage, filterType, searchKeyword]);

  const handleBack = () => {
    navigate('/admin/users');
  };

  const handleFilterChange = (type: string) => {
    setFilterType(type);
    setCurrentPage(1);
  };

  const handleSearch = (keyword: string) => {
    setSearchKeyword(keyword);
    setCurrentPage(1);
  };

  const handleViewDetail = (divination: UserDivination) => {
    setSelectedDivination(divination);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedDivination(null);
  };

  if (loading) {
    return (
      <div className="user-detail-page">
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="user-detail-page">
        <div className="error">用户不存在</div>
      </div>
    );
  }

  return (
    <div className="user-detail-page">
      <div className="page-header">
        <button className="back-btn" onClick={handleBack}>
          ← 返回用户列表
        </button>
        <h1>用户详情</h1>
      </div>

      <div className="page-content">
        {/* 用户基本信息 */}
        <UserInfoCard user={user} />

        {/* 占卜统计 */}
        <DivinationStatsCard
          totalCount={user.divination_count}
          ichingCount={user.iching_count}
          tarotCount={user.tarot_count}
          fortuneCount={user.fortune_count}
        />

        {/* 占卜历史 */}
        <DivinationHistoryList
          divinations={divinations}
          loading={divinationLoading}
          total={total}
          currentPage={currentPage}
          pageSize={10}
          filterType={filterType}
          searchKeyword={searchKeyword}
          onPageChange={setCurrentPage}
          onFilterChange={handleFilterChange}
          onSearch={handleSearch}
          onViewDetail={handleViewDetail}
        />
      </div>

      {/* 占卜详情弹窗 */}
      <DivinationDetailModal
        divination={selectedDivination}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}

