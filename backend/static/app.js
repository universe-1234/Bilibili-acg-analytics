// ====== B站ACG数据分析系统 - 主应用 JS ======

// --- State ---
var token = localStorage.getItem('token') || '';
var currentUser = null;
var currentPage = 'home';
var currentVideoId = null;

// Home state
var videos = [];
var videoTotal = 0;
var videoPage = 1;
var searchKeyword = '';
var searchCategory = '';
var searchSort = 'play_count';
var categories = [];

// Detail state
var videoDetail = null;
var comments = [];
var commentTotal = 0;
var relatedVideos = [];

// Chart instances
var chartInstances = [];

// ====== Init ======
function init() {
  if (token) {
    apiGet('/auth/me').then(function(u) {
      currentUser = u;
      updateUI();
    }).catch(function() { logout(); });
  }
  updateUI();
  navigateTo('home');

  // Handle browser back/forward
  window.addEventListener('hashchange', function() {
    var hash = window.location.hash.slice(1);
    if (hash.startsWith('video/')) {
      navigateTo('video', parseInt(hash.split('/')[1]));
    } else if (hash) {
      navigateTo(hash);
    }
  });
}

// ====== API ======
function authHeaders() {
  var h = { 'Content-Type': 'application/json' };
  if (token) h['Authorization'] = 'Bearer ' + token;
  return h;
}

async function apiGet(path) {
  var res = await fetch('/api' + path, { headers: authHeaders() });
  if (res.status === 401) { logout(); throw new Error('Unauthorized'); }
  if (!res.ok) {
    var err = await res.json().catch(function() { return {}; });
    throw new Error(err.detail || '请求失败');
  }
  return res.json();
}

async function apiPost(path, body) {
  var res = await fetch('/api' + path, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body)
  });
  if (res.status === 401) { logout(); throw new Error('Unauthorized'); }
  if (!res.ok) {
    var err = await res.json().catch(function() { return {}; });
    throw new Error(err.detail || '操作失败');
  }
  return res.json();
}

// ====== Auth ======
function logout() {
  token = '';
  currentUser = null;
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  showToast('已退出登录');
  setTimeout(function() { navigateTo('home'); }, 500);
}

// ====== Navigation ======
function navigateTo(page, id) {
  currentPage = page;
  if (page === 'video' && id) {
    currentVideoId = id;
    window.location.hash = 'video/' + id;
  } else {
    window.location.hash = page;
  }

  // Hide all sections
  var sections = document.querySelectorAll('.page-section');
  sections.forEach(function(s) { s.style.display = 'none'; });

  // Show target
  var target = document.getElementById('page-' + page);
  if (target) target.style.display = 'block';

  // Update nav active
  document.querySelectorAll('.nav-link').forEach(function(a) { a.classList.remove('active'); });
  var navEl = document.querySelector('[data-page="' + page + '"]');
  if (navEl) navEl.classList.add('active');

  updateUI();

  // Load page data
  if (page === 'home') { loadVideos(); loadCategories(); }
  if (page === 'video' && id) { loadVideoDetail(id); loadComments(id); loadRelated(id); }
  if (page === 'dashboard') { requestAnimationFrame(function() { requestAnimationFrame(function() { initDashboardCharts(); }); }); }
  if (page === 'bigscreen') { requestAnimationFrame(function() { requestAnimationFrame(function() { initBigScreenCharts(); }); }); }
  if (page === 'favorites') { loadFavorites(); }

  window.scrollTo(0, 0);
}

function updateUI() {
  var loggedIn = !!token;
  var navAuth = document.getElementById('nav-auth');
  var favoritesLink = document.getElementById('favorites-link');

  if (loggedIn && currentUser) {
    navAuth.innerHTML = '<span style="color:#888;font-size:14px;margin-right:12px">' + (currentUser.nickname || currentUser.username) + '</span><button class="nav-btn" onclick="logout()">退出</button>';
    if (favoritesLink) favoritesLink.style.display = '';
  } else {
    navAuth.innerHTML = '<button class="nav-btn" onclick="window.location.href=\'/login.html\'">登录</button><button class="nav-btn nav-btn-primary" onclick="window.location.href=\'/login.html\'">注册</button>';
    if (favoritesLink) favoritesLink.style.display = 'none';
  }
}

// ====== Toast ======
function showToast(msg) {
  var t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);padding:10px 24px;background:#f472b6;color:#fff;border-radius:8px;z-index:9999;font-size:14px;box-shadow:0 4px 20px rgba(244,114,182,0.4)';
  document.body.appendChild(t);
  setTimeout(function() { t.remove(); }, 2500);
}

// ====== Format ======
function fmtNum(n) {
  if (!n) return '0';
  if (n >= 100000000) return (n/100000000).toFixed(1) + '亿';
  if (n >= 10000) return (n/10000).toFixed(1) + '万';
  return Number(n).toLocaleString();
}

// ====== Home Page ======
async function loadVideos(page) {
  page = page || 1;
  videoPage = page;
  var params = '?page=' + page + '&page_size=20&sort_by=' + searchSort;
  if (searchKeyword) params += '&keyword=' + encodeURIComponent(searchKeyword);
  if (searchCategory) params += '&category=' + encodeURIComponent(searchCategory);

  try {
    var data = await apiGet('/videos' + params);
    videos = data.items;
    videoTotal = data.total;
    renderVideoGrid();
  } catch(e) {
    document.getElementById('video-grid').innerHTML = '<div style="text-align:center;padding:40px;color:#888">加载失败: ' + e.message + '</div>';
  }
}

async function loadCategories() {
  try {
    categories = await apiGet('/videos/categories');
    var sel = document.getElementById('cat-select');
    sel.innerHTML = '<option value="">全部分类</option>';
    categories.forEach(function(c) {
      sel.innerHTML += '<option value="' + c + '">' + c + '</option>';
    });
  } catch(e) {}
}

function renderVideoGrid() {
  var html = '';
  videos.forEach(function(v) {
    html += '<div class="video-card" onclick="navigateTo(\'video\',' + v.id + ')">';
    html += '<div class="cover"><img src="' + v.cover_url + '" alt="" loading="lazy"><span class="dur">' + v.duration + '</span><span class="cat">' + (v.category || 'ACG') + '</span></div>';
    html += '<div class="vinfo"><h3>' + escapeHtml(v.title) + '</h3><div class="author">' + escapeHtml(v.author_name) + '</div>';
    html += '<div class="vstats"><span>▶ ' + fmtNum(v.play_count) + '</span><span>💬 ' + fmtNum(v.danmaku_count) + '</span><span>👍 ' + fmtNum(v.like_count) + '</span></div></div></div>';
  });
  document.getElementById('video-grid').innerHTML = html || '<div style="text-align:center;padding:60px;color:#666;grid-column:1/-1">暂无视频数据</div>';

  var hint = document.getElementById('video-total-hint');
  if (hint) hint.textContent = '共 ' + videoTotal + ' 个视频';

  // Pagination
  var pagEl = document.getElementById('pagination');
  if (videoTotal > 20) {
    var totalPages = Math.ceil(videoTotal / 20);
    var pagHtml = '';
    for (var i = 1; i <= Math.min(totalPages, 15); i++) {
      pagHtml += '<button class="page-btn' + (i === videoPage ? ' active' : '') + '" onclick="loadVideos(' + i + ')">' + i + '</button>';
    }
    if (totalPages > 15) pagHtml += '<span style="color:#666">...' + totalPages + '</span>';
    pagEl.innerHTML = pagHtml;
  } else {
    pagEl.innerHTML = '';
  }
}

function searchVideos() {
  searchKeyword = document.getElementById('search-input').value;
  searchCategory = document.getElementById('cat-select').value;
  searchSort = document.getElementById('sort-select').value;
  loadVideos(1);
}

// ====== Video Detail ======
async function loadVideoDetail(id) {
  try {
    videoDetail = await apiGet('/videos/' + id);
    renderVideoDetail();
  } catch(e) {
    document.getElementById('detail-content').innerHTML = '<div style="text-align:center;padding:40px;color:#888">加载失败</div>';
  }
}

function renderVideoDetail() {
  var v = videoDetail;
  var html = '';

  // Cover + Player
  html += '<div class="player-area" onclick="window.open(\'' + v.bilibili_url + '\',\'_blank\')">';
  html += '<img src="' + v.cover_url + '" alt=""><div class="play-overlay"><div style="font-size:48px">▶️</div><div style="margin-top:12px">点击跳转B站播放</div></div>';
  html += '</div>';

  // Title & meta
  html += '<h2 style="font-size:22px;margin:16px 0 8px">' + escapeHtml(v.title) + '</h2>';
  html += '<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-bottom:16px">';
  html += '<span style="color:#f472b6">' + escapeHtml(v.author_name) + '</span>';
  html += '<span style="color:#888">' + (v.category || '') + '</span>';
  html += '<span style="color:#666">' + (v.publish_date || '').split('T')[0] + '</span>';
  html += '<button class="nav-btn" onclick="toggleFavorite(' + v.id + ')">' + (v.is_favorited ? '⭐ 已收藏' : '☆ 收藏') + '</button>';
  html += '<button class="nav-btn" onclick="window.open(\'' + v.bilibili_url + '\',\'_blank\')">🔗 B站原视频</button>';
  html += '</div>';

  // Stats row
  html += '<div class="stats-row">';
  var stats = [['播放', fmtNum(v.play_count)], ['弹幕', fmtNum(v.danmaku_count)], ['点赞', fmtNum(v.like_count)], ['投币', fmtNum(v.coin_count)], ['收藏', fmtNum(v.favorite_count)], ['分享', fmtNum(v.share_count)], ['评论', fmtNum(v.reply_count)]];
  stats.forEach(function(s) { html += '<div class="stat-card"><div class="sval">' + s[1] + '</div><div class="slbl">' + s[0] + '</div></div>'; });
  html += '</div>';

  // Tags
  if (v.tags) {
    html += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px">';
    v.tags.split(',').filter(Boolean).forEach(function(t) {
      html += '<span class="tag">' + t.trim() + '</span>';
    });
    html += '</div>';
  }

  // Description
  html += '<div class="desc-box"><h3>视频简介</h3><p>' + (v.description || '暂无简介') + '</p></div>';

  document.getElementById('detail-content').innerHTML = html;
}

async function toggleFavorite(id) {
  if (!token) { showToast('请先登录'); return; }
  try {
    var res = await apiPost('/videos/' + id + '/favorite');
    videoDetail.is_favorited = res.favorited;
    showToast(res.favorited ? '已收藏' : '已取消收藏');
    renderVideoDetail();
  } catch(e) { showToast(e.message); }
}

// ====== Comments ======
async function loadComments(videoId) {
  try {
    var data = await apiGet('/videos/' + videoId + '/comments?page=1&page_size=50');
    comments = data.items;
    commentTotal = data.total;
    renderComments();
  } catch(e) {}
}

function renderComments() {
  document.getElementById('comment-count').textContent = commentTotal;
  var html = '';
  comments.forEach(function(c) {
    html += '<div class="comment-item"><span class="cuser">' + escapeHtml(c.nickname || c.username) + '</span><span class="ctime">' + (c.created_at || '').split('T')[0] + '</span><div class="ctext">' + escapeHtml(c.content) + '</div></div>';
  });
  document.getElementById('comment-list').innerHTML = html || '<div style="text-align:center;padding:24px;color:#666">暂无评论</div>';

  var formArea = document.getElementById('comment-form-area');
  var loginPrompt = document.getElementById('comment-login-prompt');
  if (formArea) formArea.style.display = token ? 'block' : 'none';
  if (loginPrompt) loginPrompt.style.display = token ? 'none' : 'block';
}

async function submitComment() {
  if (!token) { showToast('请先登录'); return; }
  var text = document.getElementById('comment-input').value.trim();
  if (!text) { showToast('请输入评论内容'); return; }
  try {
    await apiPost('/videos/' + currentVideoId + '/comments', { content: text });
    document.getElementById('comment-input').value = '';
    showToast('评论发表成功');
    loadComments(currentVideoId);
  } catch(e) { showToast(e.message); }
}

// ====== Related Videos ======
async function loadRelated(id) {
  try {
    if (!videoDetail || !videoDetail.category) return;
    var data = await apiGet('/videos?category=' + encodeURIComponent(videoDetail.category) + '&page_size=6&sort_by=play_count');
    relatedVideos = data.items.filter(function(v) { return v.id !== id; }).slice(0, 5);
    var html = '<h3 style="margin-bottom:16px">相关推荐</h3>';
    relatedVideos.forEach(function(v) {
      html += '<div class="related-card" onclick="navigateTo(\'video\',' + v.id + ')">';
      html += '<img src="' + v.cover_url + '" alt=""><div class="rel-info"><div class="rel-title">' + escapeHtml(v.title) + '</div><div class="rel-author">' + escapeHtml(v.author_name) + '</div><div class="rel-plays">' + fmtNum(v.play_count) + ' 播放</div></div></div>';
    });
    document.getElementById('related-list').innerHTML = html;
  } catch(e) {}
}

// ====== Favorites ======
async function loadFavorites() {
  if (!token) return;
  try {
    var data = await apiGet('/user/favorites?page=1&page_size=100');
    var html = '';
    data.items.forEach(function(v) {
      html += '<div class="video-card" onclick="navigateTo(\'video\',' + v.id + ')"><div class="cover"><img src="' + v.cover_url + '" alt=""><span class="dur">' + v.duration + '</span></div><div class="vinfo"><h3>' + escapeHtml(v.title) + '</h3><div class="author">' + escapeHtml(v.author_name) + '</div></div></div>';
    });
    document.getElementById('fav-grid').innerHTML = html || '<div style="text-align:center;padding:80px;color:#666;grid-column:1/-1"><div style="font-size:48px">⭐</div><div style="margin:16px">还没有收藏</div><button class="nav-btn nav-btn-primary" onclick="navigateTo(\'home\')">去发现视频</button></div>';
  } catch(e) {}
}

// ====== Charts (Dashboard) ======
function makeChart(domId, option) {
  var dom = document.getElementById(domId);
  if (!dom) return null;
  // Dispose existing
  dom.innerHTML = '';
  var chart = echarts.init(dom);
  chart.setOption(option);
  chartInstances.push(chart);
  return chart;
}

var chartColors = ['#f472b6','#a78bfa','#60a5fa','#34d399','#fbbf24','#f87171','#818cf8','#2dd4bf','#fb923c','#a3e635'];

function baseOption() {
  return {
    tooltip: { backgroundColor: '#1a1a2e', borderColor: '#2a2a4e', textStyle: { color: '#e0e0e0' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true }
  };
}

async function initDashboardCharts() {
  if (typeof echarts === "undefined") { console.error("ECharts not loaded"); return; }
  chartInstances.forEach(function(c) { c.dispose(); });
  chartInstances = [];

  // Overview
  try {
    var d = await apiGet('/dashboard/overview');
    document.getElementById('dash-overview').innerHTML = [
      ['视频总数', d.total_videos], ['用户总数', d.total_users], ['评论总数', d.total_comments],
      ['总播放量', fmtNum(d.total_plays)], ['总点赞数', fmtNum(d.total_likes)], ['总弹幕数', fmtNum(d.total_danmaku)], ['收藏总数', fmtNum(d.total_favorites)]
    ].map(function(s) { return '<div class="stat-card"><div class="sval">' + s[1] + '</div><div class="slbl">' + s[0] + '</div></div>'; }).join('');
  } catch(e) {}

  // Category Pie
  try {
    var cats = await apiGet('/dashboard/category-stats');
    makeChart('chart-cat', {
      ...baseOption(),
      series: [{ type: 'pie', radius: ['40%','70%'], roseType: 'radius', itemStyle: { borderRadius: 6, borderColor: '#1a1a2e', borderWidth: 2 }, label: { color: '#aaa' }, data: cats.map(function(c) { return { name: c.category, value: c.count }; }) }],
      color: chartColors
    });
  } catch(e) {}

  // Top Videos
  try {
    var top = await apiGet('/dashboard/top-videos?limit=15');
    var rev = top.slice().reverse();
    makeChart('chart-top', {
      ...baseOption(),
      xAxis: { type: 'value', axisLabel: { color: '#888', fontSize: 10, formatter: fmtNum }, splitLine: { lineStyle: { color: '#1a1a2e' } } },
      yAxis: { type: 'category', data: rev.map(function(v) { return v.title.slice(0,12) + (v.title.length>12?'…':''); }), axisLabel: { color: '#aaa', fontSize: 10 }, axisLine: { show: false }, axisTick: { show: false } },
      series: [{ type: 'bar', data: rev.map(function(v) { return { value: v.play_count, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f472b6'},{offset:1,color:'#a78bfa'}]), borderRadius: [0,4,4,0] } }; }), label: { show: true, position: 'right', color: '#aaa', fontSize: 10, formatter: function(p) { return fmtNum(p.value); } } }]
    });
  } catch(e) {}

  // Trends
  try {
    var trend = await apiGet('/dashboard/daily-trends?days=30');
    makeChart('chart-trend', {
      ...baseOption(),
      legend: { textStyle: { color: '#888' }, top: 0 },
      xAxis: { type: 'category', data: trend.map(function(d) { return d.date; }), axisLabel: { color: '#666', fontSize: 10 } },
      yAxis: { type: 'value', axisLabel: { color: '#666', formatter: fmtNum }, splitLine: { lineStyle: { color: '#1a1a2e' } } },
      series: ['plays','likes','danmaku'].map(function(k,i) { return { name: {plays:'播放',likes:'点赞',danmaku:'弹幕'}[k], type: 'line', data: trend.map(function(d) { return d[k]; }), smooth: true, symbol: 'none', lineStyle: {width:2}, color: chartColors[i] }; })
    });
  } catch(e) {}

  // Authors
  try {
    var authors = await apiGet('/dashboard/author-ranking');
    makeChart('chart-auth', {
      ...baseOption(),
      xAxis: { type: 'category', data: authors.map(function(a) { return a.author; }), axisLabel: { color: '#666', fontSize: 10, rotate: 30 } },
      yAxis: { type: 'value', axisLabel: { color: '#666', formatter: fmtNum }, splitLine: { lineStyle: { color: '#1a1a2e' } } },
      series: [{ type: 'bar', data: authors.map(function(a) { return a.total_plays; }), itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#60a5fa'},{offset:1,color:'#a78bfa'}]), borderRadius: [6,6,0,0] } }]
    });
  } catch(e) {}

  // Tags
  try {
    var tags = await apiGet('/dashboard/tag-cloud');
    var topTags = tags.slice(0,15);
    makeChart('chart-tags', {
      ...baseOption(),
      grid: { left: '3%', right: '10%', top: 5, bottom: 5, containLabel: true },
      xAxis: { type: 'value', axisLabel: { color: '#666', fontSize: 10 }, splitLine: { lineStyle: { color: '#1a1a2e' } } },
      yAxis: { type: 'category', data: topTags.map(function(t) { return t.name; }).reverse(), axisLabel: { color: '#888', fontSize: 11 }, axisLine: { show: false }, axisTick: { show: false } },
      series: [{ type: 'bar', data: topTags.map(function(t,i) { return { value: t.value, itemStyle: { color: chartColors[i%chartColors.length], borderRadius: [0,4,4,0] } }; }).reverse() }]
    });
  } catch(e) {}

  // Publish Trends
  try {
    var pub = await apiGet('/dashboard/publish-trends');
    makeChart('chart-pub', {
      ...baseOption(),
      xAxis: { type: 'category', data: pub.map(function(d) { return d.date; }), axisLabel: { color: '#666', fontSize: 10 } },
      yAxis: { type: 'value', axisLabel: { color: '#666' }, splitLine: { lineStyle: { color: '#1a1a2e' } } },
      series: [{ type: 'bar', data: pub.map(function(d) { return d.count; }), itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#34d399'},{offset:1,color:'#60a5fa'}]), borderRadius: [4,4,0,0] } }]
    });
  } catch(e) {}
}

// ====== Big Screen Charts ======
async function initBigScreenCharts() {
  if (typeof echarts === "undefined") { console.error("ECharts not loaded"); return; }
  chartInstances.forEach(function(c) { c.dispose(); });
  chartInstances = [];

  try {
    var d = await apiGet('/dashboard/overview');
    document.getElementById('big-overview').innerHTML = [
      ['视频总数', d.total_videos], ['总播放量', fmtNum(d.total_plays)], ['总点赞数', fmtNum(d.total_likes)], ['总弹幕数', fmtNum(d.total_danmaku)]
    ].map(function(s) { return '<div class="stat-card"><div class="sval" style="color:#00d4ff;font-size:18px">' + s[1] + '</div><div class="slbl">' + s[0] + '</div></div>'; }).join('');
  } catch(e) {}

  var bc = ['#00d4ff','#f472b6','#a78bfa','#34d399','#fbbf24','#f87171','#60a5fa'];

  try {
    var cats = await apiGet('/dashboard/category-stats');
    makeChart('big-pie', { ...baseOption(),
      series: [{ type: 'pie', radius: ['35%','60%'], label: { color: '#aaa', fontSize:10, formatter:'{b}\n{d}%' }, data: cats.map(function(c) { return { name:c.category, value:c.count }; }) }], color: bc });
  } catch(e) {}

  try {
    var tags = await apiGet('/dashboard/tag-cloud');
    var tt = tags.slice(0,12);
    makeChart('big-tags', {
      ...baseOption(), grid: { left:'3%',right:'10%',top:5,bottom:5,containLabel:true },
      xAxis: { type:'value', axisLabel:{color:'#555',fontSize:9}, splitLine:{lineStyle:{color:'#151530'}} },
      yAxis: { type:'category', data: tt.map(function(t){return t.name;}).reverse(), axisLabel:{color:'#888',fontSize:10}, axisLine:{show:false}, axisTick:{show:false} },
      series: [{ type:'bar', data: tt.map(function(t){return t.value;}).reverse(), itemStyle:{ color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f472b6'},{offset:1,color:'#fbbf24'}]), borderRadius:[0,3,3,0] } }]
    });
  } catch(e) {}

  try {
    var top = await apiGet('/dashboard/top-videos?limit=20');
    var td = top.slice().reverse();
    makeChart('big-top', {
      ...baseOption(), grid: { left:'2%',right:'12%',top:10,bottom:5,containLabel:true },
      yAxis: { type:'category', data: td.map(function(v){return v.title.slice(0,10)+(v.title.length>10?'…':'');}), axisLabel:{color:'#aaa',fontSize:10}, axisLine:{show:false}, axisTick:{show:false}, inverse:true },
      xAxis: { type:'value', axisLabel:{color:'#888',fontSize:9,formatter:fmtNum}, splitLine:{lineStyle:{color:'#151530'}} },
      series: [{ type:'bar', data: td.map(function(v){ return { value:v.play_count, itemStyle:{ color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#a78bfa'},{offset:1,color:'#00d4ff'}]), borderRadius:[0,4,4,0] } }; }), label:{show:true,position:'right',color:'#aaa',fontSize:10,formatter:function(p){return fmtNum(p.value);}} }]
    });
  } catch(e) {}

  try {
    var trend = await apiGet('/dashboard/daily-trends?days=30');
    makeChart('big-trend', {
      ...baseOption(), grid:{left:'5%',right:'5%',top:20,bottom:5,containLabel:true},
      legend:{textStyle:{color:'#888',fontSize:10},top:0},
      xAxis:{type:'category',data:trend.map(function(d){return d.date.slice(5);}),axisLabel:{color:'#555',fontSize:9}},
      yAxis:{type:'value',axisLabel:{color:'#555',fontSize:9,formatter:fmtNum},splitLine:{lineStyle:{color:'#151530'}}},
      series:['plays','likes','danmaku'].map(function(k,i){return{name:{plays:'播放',likes:'点赞',danmaku:'弹幕'}[k],type:'line',data:trend.map(function(d){return d[k];}),smooth:true,symbol:'none',lineStyle:{width:2},color:bc[i]};})
    });
  } catch(e) {}

  try {
    var authors = await apiGet('/dashboard/author-ranking');
    var ad = authors.slice(0,10).reverse();
    makeChart('big-auth', {
      ...baseOption(), grid:{left:'3%',right:'10%',top:5,bottom:5,containLabel:true},
      yAxis:{type:'category',data:ad.map(function(a){return a.author;}),axisLabel:{color:'#888',fontSize:9},axisLine:{show:false},axisTick:{show:false}},
      xAxis:{type:'value',axisLabel:{color:'#555',fontSize:9,formatter:fmtNum},splitLine:{lineStyle:{color:'#151530'}}},
      series:[{type:'bar',data:ad.map(function(a){return a.total_plays;}),itemStyle:{color:new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#f97316'},{offset:1,color:'#fbbf24'}]),borderRadius:[0,3,3,0]}}]
    });
  } catch(e) {}

  try {
    var pub = await apiGet('/dashboard/publish-trends');
    makeChart('big-pub', {
      ...baseOption(), grid:{left:'3%',right:'5%',top:5,bottom:5,containLabel:true},
      xAxis:{type:'category',data:pub.map(function(d){return d.date.slice(5);}),axisLabel:{color:'#555',fontSize:8}},
      yAxis:{type:'value',axisLabel:{color:'#555',fontSize:9},splitLine:{lineStyle:{color:'#151530'}}},
      series:[{type:'bar',data:pub.map(function(d){return d.count;}),itemStyle:{color:new echarts.graphic.LinearGradient(0,0,0,1,[{offset:0,color:'#60a5fa'},{offset:1,color:'#34d399'}]),borderRadius:[3,3,0,0]}}]
    });
  } catch(e) {}

  try {
    var engage = await apiGet('/dashboard/video-engagement');
    var totals = {plays:0,likes:0,danmaku:0,favorites:0,shares:0,coins:0};
    engage.forEach(function(v){totals.plays+=v.plays;totals.likes+=v.likes;totals.danmaku+=v.danmaku;totals.favorites+=v.favorites;totals.shares+=v.shares;totals.coins+=v.coins;});
    makeChart('big-radar', {
      ...baseOption(),
      radar:{center:['50%','50%'],radius:'65%',indicator:[{name:'播放',max:totals.plays},{name:'点赞',max:totals.likes},{name:'弹幕',max:totals.danmaku},{name:'收藏',max:totals.favorites},{name:'分享',max:totals.shares},{name:'投币',max:totals.coins}],axisName:{color:'#888',fontSize:10}},
      series:[{type:'radar',data:[{value:[totals.plays,totals.likes,totals.danmaku,totals.favorites,totals.shares,totals.coins],name:'互动数据',areaStyle:{color:'rgba(244,114,182,0.3)'},itemStyle:{color:'#f472b6'},lineStyle:{color:'#f472b6'}}]}]
    });
  } catch(e) {}
}

// ====== Utility ======
function escapeHtml(str) {
  if (!str) return '';
  var div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ====== Init on load ======
if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", init); } else { init(); }
