/**
 * 音频平台智能选择器
 * 根据用户地理位置自动选择最适合的音频平台
 */

class AudioPlatformSelector {
    constructor() {
        this.platforms = {
            youtube: {
                name: 'YouTube',
                icon: '🎥',
                regions: ['international', 'overseas'],
                priority: { international: 1, china: 3 }
            },
            ximalaya: {
                name: '喜马拉雅',
                icon: '🎙️',
                regions: ['china', 'domestic'],
                priority: { china: 1, international: 3 }
            },
            local: {
                name: '本地音频',
                icon: '🔊',
                regions: ['all'],
                priority: { china: 2, international: 2 }
            }
        };
        
        this.userRegion = null;
        this.detectionMethods = ['geolocation', 'ip', 'timezone'];
        this.detectionComplete = false;
    }

    /**
     * 初始化地区检测
     */
    async detectUserRegion() {
        if (this.detectionComplete) {
            return this.userRegion;
        }

        // 优先尝试精确方法，然后降级到简单方法
        for (const method of this.detectionMethods) {
            try {
                const region = await this[`detect${method.charAt(0).toUpperCase() + method.slice(1)}`]();
                if (region) {
                    this.userRegion = region;
                    this.detectionComplete = true;
                    console.log(`🌍 地区检测成功 (${method}): ${region}`);
                    return region;
                }
            } catch (error) {
                console.warn(`地区检测方法 ${method} 失败:`, error);
                continue;
            }
        }

        // 如果所有方法都失败，默认为国际
        this.userRegion = 'international';
        this.detectionComplete = true;
        console.log('🌍 地区检测失败，使用默认设置: international');
        return this.userRegion;
    }

    /**
     * 基于浏览器地理位置API检测
     */
    async detectGeolocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('地理位置API不支持'));
                return;
            }

            const timeout = setTimeout(() => {
                reject(new Error('地理位置检测超时'));
            }, 5000);

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    clearTimeout(timeout);
                    const { latitude, longitude } = position.coords;
                    
                    // 简单的中国境内判断（大致边界）
                    const isInChina = (
                        latitude >= 18.0 && latitude <= 53.0 &&
                        longitude >= 73.0 && longitude <= 135.0
                    );
                    
                    resolve(isInChina ? 'china' : 'international');
                },
                (error) => {
                    clearTimeout(timeout);
                    reject(error);
                },
                { timeout: 5000, maximumAge: 300000 } // 5分钟缓存
            );
        });
    }

    /**
     * 基于IP地址检测（使用免费服务）
     */
    async detectIp() {
        try {
            // 使用免费的IP地理位置服务
            const response = await fetch('https://ipapi.co/json/', {
                method: 'GET',
                timeout: 3000
            });
            
            if (!response.ok) {
                throw new Error('IP检测服务响应失败');
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.reason || 'IP检测服务错误');
            }
            
            // 检查是否为中国IP
            const isInChina = data.country_code === 'CN' || 
                             data.country === 'China' ||
                             data.country_name === 'China';
            
            return isInChina ? 'china' : 'international';
        } catch (error) {
            // 如果主要服务失败，尝试备用服务
            try {
                const response = await fetch('https://ip.nf/me.json', {
                    method: 'GET',
                    timeout: 3000
                });
                const data = await response.json();
                const isInChina = data.ip.country_code === 'CN';
                return isInChina ? 'china' : 'international';
            } catch (backupError) {
                throw new Error('所有IP检测服务都失败了');
            }
        }
    }

    /**
     * 基于时区的简单检测（最后手段）
     */
    async detectTimezone() {
        try {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            
            // 中国时区判断
            const chineseTimezones = [
                'Asia/Shanghai',
                'Asia/Beijing',
                'Asia/Chongqing',
                'Asia/Harbin',
                'Asia/Kashgar',
                'Asia/Urumqi'
            ];
            
            const isInChina = chineseTimezones.some(tz => timezone.includes(tz));
            return isInChina ? 'china' : 'international';
        } catch (error) {
            throw new Error('时区检测失败');
        }
    }

    /**
     * 获取推荐的音频平台
     */
    getRecommendedPlatform(region = null) {
        const userRegion = region || this.userRegion || 'international';
        
        // 根据地区和优先级排序
        const sortedPlatforms = Object.entries(this.platforms)
            .map(([key, platform]) => ({
                key,
                ...platform,
                priority: platform.priority[userRegion] || 999
            }))
            .sort((a, b) => a.priority - b.priority);
        
        return sortedPlatforms[0].key;
    }

    /**
     * 获取所有可用平台（按优先级排序）
     */
    getAvailablePlatforms(region = null) {
        const userRegion = region || this.userRegion || 'international';
        
        return Object.entries(this.platforms)
            .map(([key, platform]) => ({
                key,
                ...platform,
                priority: platform.priority[userRegion] || 999
            }))
            .sort((a, b) => a.priority - b.priority);
    }

    /**
     * 显示音频播放器
     */
    renderAudioPlayer(containerId, audioData) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`容器元素未找到: ${containerId}`);
            return;
        }

        // 检测地区并渲染
        this.detectUserRegion().then(region => {
            const recommendedPlatform = this.getRecommendedPlatform(region);
            const allPlatforms = this.getAvailablePlatforms(region);
            
            container.innerHTML = this.generatePlayerHTML(audioData, recommendedPlatform, allPlatforms, region);
            this.attachEventListeners(containerId);
        });
    }

    /**
     * 生成播放器HTML
     */
    generatePlayerHTML(audioData, primaryPlatform, allPlatforms, region) {
        const regionName = region === 'china' ? '中国大陆' : '海外地区';
        
        return `
            <div class="audio-platform-selector">
                <div class="platform-indicator">
                    <span class="region-indicator">🌍 检测到您位于: ${regionName}</span>
                    <span class="recommended-label">推荐平台: ${this.platforms[primaryPlatform].icon} ${this.platforms[primaryPlatform].name}</span>
                </div>
                
                <div class="platform-tabs">
                    ${allPlatforms.map((platform, index) => `
                        <button class="platform-tab ${index === 0 ? 'active' : ''}" 
                                data-platform="${platform.key}">
                            ${platform.icon} ${platform.name}
                        </button>
                    `).join('')}
                </div>
                
                <div class="platform-content">
                    ${allPlatforms.map((platform, index) => `
                        <div class="platform-player ${index === 0 ? 'active' : ''}" 
                             data-platform="${platform.key}">
                            ${this.generatePlatformPlayer(platform.key, audioData)}
                        </div>
                    `).join('')}
                </div>
                
                <div class="platform-footer">
                    <small>💡 可以点击上方标签切换其他平台</small>
                </div>
            </div>
        `;
    }

    /**
     * 生成特定平台的播放器
     */
    generatePlatformPlayer(platform, audioData) {
        if (!audioData || !audioData.platforms || !audioData.platforms[platform]) {
            return `<p class="platform-unavailable">❌ ${this.platforms[platform].name} 暂不可用</p>`;
        }

        const platformData = audioData.platforms[platform];
        
        switch (platform) {
            case 'youtube':
                return `
                    <div class="video-container">
                        <iframe src="${platformData.embed_url}?rel=0&showinfo=0&color=white&iv_load_policy=3" 
                                frameborder="0" allowfullscreen>
                        </iframe>
                    </div>
                    <p><strong>🔗 直接链接</strong>: <a href="${platformData.direct_url}" target="_blank">在YouTube中打开</a></p>
                    <p><small>💡 此视频设为非公开，仅通过本站链接可访问</small></p>
                `;
                
            case 'ximalaya':
                return `
                    <div class="ximalaya-player">
                        <iframe src="${platformData.embed_url}" frameborder="0"></iframe>
                    </div>
                    <p><strong>🔗 直接链接</strong>: <a href="${platformData.direct_url}" target="_blank">在喜马拉雅中打开</a></p>
                `;
                
            case 'local':
                return `
                    <audio controls style="width: 100%;">
                        <source src="${platformData.file_path}" type="audio/mpeg">
                        您的浏览器不支持音频播放。
                    </audio>
                    <p><strong>📊 文件信息</strong>: ${platformData.file_size || ''} | ${audioData.metadata?.duration || ''}</p>
                `;
                
            default:
                return `<p class="platform-error">❌ 未知平台: ${platform}</p>`;
        }
    }

    /**
     * 绑定事件监听器
     */
    attachEventListeners(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // 平台切换功能
        const tabs = container.querySelectorAll('.platform-tab');
        const players = container.querySelectorAll('.platform-player');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const platform = tab.dataset.platform;
                
                // 更新激活状态
                tabs.forEach(t => t.classList.remove('active'));
                players.forEach(p => p.classList.remove('active'));
                
                tab.classList.add('active');
                const targetPlayer = container.querySelector(`[data-platform="${platform}"]`);
                if (targetPlayer) {
                    targetPlayer.classList.add('active');
                }
                
                // 记录用户选择（用于分析）
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'platform_switch', {
                        'platform': platform,
                        'user_region': this.userRegion
                    });
                }
            });
        });
    }
}

// 全局实例
window.AudioPlatformSelector = new AudioPlatformSelector();

// DOM加载完成后自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 预先检测用户地区
    window.AudioPlatformSelector.detectUserRegion();
});