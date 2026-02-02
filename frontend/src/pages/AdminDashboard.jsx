import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Plus,
  Pencil,
  Trash2,
  Upload,
  LogOut,
  Search,
  Music,
  Users,
  FileSpreadsheet,
  Youtube,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [videos, setVideos] = useState([]);
  const [stats, setStats] = useState({ total_videos: 0, total_artists: 0 });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    song: "",
    artist: "",
    youtube_url: "",
  });

  // Get auth header
  const getAuthHeader = () => {
    const auth = sessionStorage.getItem("adminAuth");
    if (!auth) {
      navigate("/admin");
      return null;
    }
    return {
      Authorization: `Basic ${btoa(`admin:${atob(auth)}`)}`,
    };
  };

  const fetchVideos = useCallback(async () => {
    const headers = getAuthHeader();
    if (!headers) return;

    try {
      const response = await axios.get(`${API}/videos`, {
        params: { search: searchQuery || undefined },
      });
      setVideos(response.data.videos);
    } catch (error) {
      console.error("Error fetching videos:", error);
    }
  }, [searchQuery]);

  const fetchStats = useCallback(async () => {
    const headers = getAuthHeader();
    if (!headers) return;

    try {
      const response = await axios.get(`${API}/admin/stats`, { headers });
      setStats(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        navigate("/admin");
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchVideos();
    fetchStats();
  }, [fetchVideos, fetchStats]);

  const handleAddVideo = async (e) => {
    e.preventDefault();
    const headers = getAuthHeader();
    if (!headers) return;

    try {
      await axios.post(`${API}/admin/videos`, formData, { headers });
      toast.success("Video added successfully!");
      setShowAddModal(false);
      setFormData({ song: "", artist: "", youtube_url: "" });
      fetchVideos();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to add video");
    }
  };

  const handleEditVideo = async (e) => {
    e.preventDefault();
    const headers = getAuthHeader();
    if (!headers || !selectedVideo) return;

    try {
      await axios.put(`${API}/admin/videos/${selectedVideo.id}`, formData, { headers });
      toast.success("Video updated successfully!");
      setShowEditModal(false);
      setSelectedVideo(null);
      setFormData({ song: "", artist: "", youtube_url: "" });
      fetchVideos();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update video");
    }
  };

  const handleDeleteVideo = async () => {
    const headers = getAuthHeader();
    if (!headers || !selectedVideo) return;

    try {
      await axios.delete(`${API}/admin/videos/${selectedVideo.id}`, { headers });
      toast.success("Video deleted successfully!");
      setShowDeleteDialog(false);
      setSelectedVideo(null);
      fetchVideos();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete video");
    }
  };

  const handleBulkImport = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const headers = getAuthHeader();
    if (!headers) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API}/admin/videos/bulk`, formData, {
        headers: {
          ...headers,
          "Content-Type": "multipart/form-data",
        },
      });
      toast.success(response.data.message);
      if (response.data.errors?.length > 0) {
        response.data.errors.forEach((err) => toast.error(err));
      }
      setShowBulkModal(false);
      fetchVideos();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to import videos");
    }
  };

  const openEditModal = (video) => {
    setSelectedVideo(video);
    setFormData({
      song: video.song,
      artist: video.artist,
      youtube_url: video.youtube_url,
    });
    setShowEditModal(true);
  };

  const openDeleteDialog = (video) => {
    setSelectedVideo(video);
    setShowDeleteDialog(true);
  };

  const handleLogout = () => {
    sessionStorage.removeItem("adminAuth");
    navigate("/admin");
  };

  const handleYouTubeSync = async () => {
    const headers = getAuthHeader();
    if (!headers) return;

    setSyncing(true);
    try {
      const response = await axios.post(
        `${API}/admin/youtube/sync`,
        { channel_id: "UCLN8LV-ojTQP2wPtDg1kvGQ" },
        { headers }
      );
      toast.success(response.data.message);
      fetchVideos();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to sync from YouTube");
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <img src={LOGO_URL} alt="Loading" className="w-32 h-auto animate-pulse" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-background border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <img src={LOGO_URL} alt="DadRock Tabs" className="h-12 w-auto" />
              <div>
                <h1 className="font-heading text-xl font-bold uppercase tracking-tight text-white">
                  Admin Dashboard
                </h1>
                <p className="text-sm text-muted-foreground">Manage your video database</p>
              </div>
            </div>
            <Button
              variant="ghost"
              onClick={handleLogout}
              className="text-muted-foreground hover:text-white"
              data-testid="logout-button"
            >
              <LogOut className="w-5 h-5 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-card rounded-xl border border-white/5 p-6" data-testid="total-videos-stat">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Music className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-widest">Total Videos</p>
                <p className="font-heading text-3xl font-bold text-white">{stats.total_videos}</p>
              </div>
            </div>
          </div>
          <div className="bg-card rounded-xl border border-white/5 p-6" data-testid="total-artists-stat">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                <Users className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground uppercase tracking-widest">Total Artists</p>
                <p className="font-heading text-3xl font-bold text-white">{stats.total_artists}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search videos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-12 bg-secondary border-white/10 rounded-lg pl-12 text-white placeholder:text-muted-foreground"
              data-testid="admin-search-input"
            />
          </div>
          <div className="flex gap-3">
            <Button
              onClick={handleYouTubeSync}
              disabled={syncing}
              className="h-12 bg-red-600 hover:bg-red-700 text-white"
              data-testid="youtube-sync-button"
            >
              {syncing ? (
                <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
              ) : (
                <Youtube className="w-5 h-5 mr-2" />
              )}
              {syncing ? "Syncing..." : "Sync YouTube"}
            </Button>
            <Button
              onClick={() => setShowBulkModal(true)}
              variant="outline"
              className="h-12 border-white/10 text-white hover:bg-white/5"
              data-testid="bulk-import-button"
            >
              <Upload className="w-5 h-5 mr-2" />
              Bulk Import
            </Button>
            <Button
              onClick={() => {
                setFormData({ song: "", artist: "", youtube_url: "" });
                setShowAddModal(true);
              }}
              className="h-12 bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid="add-video-button"
            >
              <Plus className="w-5 h-5 mr-2" />
              Add Video
            </Button>
          </div>
        </div>

        {/* Videos Table */}
        <div className="bg-card rounded-xl border border-white/5 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="border-white/5 hover:bg-transparent">
                <TableHead className="text-muted-foreground font-heading uppercase tracking-widest">
                  Thumbnail
                </TableHead>
                <TableHead className="text-muted-foreground font-heading uppercase tracking-widest">
                  Song
                </TableHead>
                <TableHead className="text-muted-foreground font-heading uppercase tracking-widest">
                  Artist
                </TableHead>
                <TableHead className="text-muted-foreground font-heading uppercase tracking-widest text-right">
                  Actions
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {videos.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-12">
                    <Music className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No videos found</p>
                  </TableCell>
                </TableRow>
              ) : (
                videos.map((video) => (
                  <TableRow
                    key={video.id}
                    className="border-white/5 table-row-hover"
                    data-testid={`video-row-${video.id}`}
                  >
                    <TableCell>
                      <img
                        src={video.thumbnail || "https://img.youtube.com/vi/default/mqdefault.jpg"}
                        alt={video.song}
                        className="w-24 h-14 object-cover rounded-md"
                      />
                    </TableCell>
                    <TableCell className="font-medium text-white">{video.song}</TableCell>
                    <TableCell className="text-muted-foreground">{video.artist}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openEditModal(video)}
                          className="text-muted-foreground hover:text-primary"
                          data-testid={`edit-video-${video.id}`}
                        >
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openDeleteDialog(video)}
                          className="text-muted-foreground hover:text-destructive"
                          data-testid={`delete-video-${video.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </main>

      {/* Add Video Modal */}
      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent className="bg-card border-white/10">
          <DialogHeader>
            <DialogTitle className="font-heading text-xl uppercase tracking-tight text-white">
              Add New Video
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Fill in the details to add a new video to the database.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAddVideo} className="space-y-4" data-testid="add-video-form">
            <div className="space-y-2">
              <Label htmlFor="song" className="text-white">Song Name</Label>
              <Input
                id="song"
                value={formData.song}
                onChange={(e) => setFormData({ ...formData, song: e.target.value })}
                className="bg-secondary border-white/10 text-white"
                placeholder="Enter song name"
                required
                data-testid="song-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="artist" className="text-white">Artist</Label>
              <Input
                id="artist"
                value={formData.artist}
                onChange={(e) => setFormData({ ...formData, artist: e.target.value })}
                className="bg-secondary border-white/10 text-white"
                placeholder="Enter artist name"
                required
                data-testid="artist-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="youtube_url" className="text-white">YouTube URL</Label>
              <Input
                id="youtube_url"
                value={formData.youtube_url}
                onChange={(e) => setFormData({ ...formData, youtube_url: e.target.value })}
                className="bg-secondary border-white/10 text-white"
                placeholder="https://youtube.com/watch?v=..."
                required
                data-testid="youtube-url-input"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-primary text-primary-foreground" data-testid="save-video-button">
                Add Video
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Video Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="bg-card border-white/10">
          <DialogHeader>
            <DialogTitle className="font-heading text-xl uppercase tracking-tight text-white">
              Edit Video
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Update the video details below.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEditVideo} className="space-y-4" data-testid="edit-video-form">
            <div className="space-y-2">
              <Label htmlFor="edit-song" className="text-white">Song Name</Label>
              <Input
                id="edit-song"
                value={formData.song}
                onChange={(e) => setFormData({ ...formData, song: e.target.value })}
                className="bg-secondary border-white/10 text-white"
                required
                data-testid="edit-song-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-artist" className="text-white">Artist</Label>
              <Input
                id="edit-artist"
                value={formData.artist}
                onChange={(e) => setFormData({ ...formData, artist: e.target.value })}
                className="bg-secondary border-white/10 text-white"
                required
                data-testid="edit-artist-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-youtube_url" className="text-white">YouTube URL</Label>
              <Input
                id="edit-youtube_url"
                value={formData.youtube_url}
                onChange={(e) => setFormData({ ...formData, youtube_url: e.target.value })}
                className="bg-secondary border-white/10 text-white"
                required
                data-testid="edit-youtube-url-input"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setShowEditModal(false)}>
                Cancel
              </Button>
              <Button type="submit" className="bg-primary text-primary-foreground" data-testid="update-video-button">
                Update Video
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent className="bg-card border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Delete Video</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{selectedVideo?.song}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-white/10">Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteVideo}
              className="bg-destructive text-destructive-foreground"
              data-testid="confirm-delete-button"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Bulk Import Modal */}
      <Dialog open={showBulkModal} onOpenChange={setShowBulkModal}>
        <DialogContent className="bg-card border-white/10">
          <DialogHeader>
            <DialogTitle className="font-heading text-xl uppercase tracking-tight text-white">
              Bulk Import Videos
            </DialogTitle>
            <DialogDescription className="text-muted-foreground">
              Upload a CSV file with your video data.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="p-4 bg-secondary rounded-lg">
              <p className="text-sm text-muted-foreground mb-2">CSV Format Required:</p>
              <code className="text-xs text-primary">song,artist,youtube_url</code>
            </div>
            <div className="border-2 border-dashed border-white/10 rounded-lg p-8 text-center">
              <FileSpreadsheet className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <label className="cursor-pointer">
                <span className="text-primary hover:underline">Click to upload</span>
                <span className="text-muted-foreground"> or drag and drop</span>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleBulkImport}
                  className="hidden"
                  data-testid="csv-file-input"
                />
              </label>
              <p className="text-sm text-muted-foreground mt-2">CSV files only</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminDashboard;
