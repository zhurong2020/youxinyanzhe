"""
系统管理菜单处理器
负责系统配置和管理相关功能的用户界面和交互处理
遵循重构后的分层架构原则
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

from scripts.cli.base_menu_handler import BaseMenuHandler
from scripts.core.content_pipeline import ContentPipeline


class SystemMenuHandler(BaseMenuHandler):
    """系统管理菜单处理器"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化系统菜单处理器
        
        Args:
            pipeline: 内容管道实例
        """
        super().__init__(pipeline, "系统管理")
    
    def handle_llm_engine_menu(self) -> Optional[str]:
        """
        处理LLM引擎切换菜单
        
        Returns:
            处理结果或None
        """
        menu_title = "🤖 LLM引擎切换管理"
        menu_description = "💡 管理AI引擎使用模式和配置"
        
        # 检查当前状态
        status_info = self._get_current_engine_status()
        
        print(f"\n📊 当前状态:")
        print(f"   • 当前引擎: {status_info['engine']}")
        print(f"   • 引擎状态: {status_info['status']}")
        print(f"   • 模型信息: {status_info['model_info']}")
        
        print("\n💡 使用模式说明：")
        print("   • Claude: 使用您的Claude Pro订阅 ($20/月)")
        print("   • 千问3-code: 备用API引擎 (阿里云)")
        print("   • Kimi K2: 备用API引擎 (月之暗面, 高性价比)")
        print("\n⚠️  注意事项：")
        print("   • 当Claude Pro达到月度限制时，可切换到备用引擎")
        print("   • 备用引擎按使用量付费，适合突发需求")
        
        options = [
            "1. 🏠 恢复Claude Pro模式 (默认)",
            "2. 🔄 切换到千问3-code引擎",
            "3. 🌙 切换到Kimi K2引擎",
            "4. 📋 查看引擎配置详情",
            "5. 🧪 测试当前引擎连接",
            "6. 🔧 重置引擎配置",
            "7. 📝 生成WSL环境变量设置脚本"
        ]
        
        handlers = [
            self._restore_claude_pro_mode,
            self._switch_to_qwen_engine,
            self._switch_to_kimi_engine,
            self._show_engine_config_details,
            self._test_current_engine_connection,
            self._reset_engine_config,
            self._generate_wsl_env_script
        ]
        
        return self.create_menu_loop(menu_title, menu_description, options, handlers)
    
    def _get_current_engine_status(self) -> Dict[str, str]:
        """获取当前引擎状态信息"""
        current_base_url = os.getenv('ANTHROPIC_BASE_URL', '')
        current_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        if current_base_url and 'dashscope.aliyuncs.com' in current_base_url:
            return {
                'engine': "千问3-code (Qwen)",
                'status': "🟢 活跃",
                'model_info': "qwen3-code (1万亿参数MoE)"
            }
        elif current_base_url and 'moonshot.ai' in current_base_url:
            return {
                'engine': "Kimi K2 (Moonshot)",
                'status': "🟢 活跃", 
                'model_info': "kimi-k2 (1万亿参数MoE, 128K上下文)"
            }
        elif current_api_key:
            return {
                'engine': "Claude Pro (官方)",
                'status': "🟢 活跃",
                'model_info': "claude-3.5-sonnet (官方API)"
            }
        else:
            return {
                'engine': "Claude Pro (默认)",
                'status': "🟡 默认模式",
                'model_info': "claude-3.5-sonnet (无API配置)"
            }
    
    def _restore_claude_pro_mode(self) -> Optional[str]:
        """恢复Claude Pro模式"""
        self.display_menu_header("🏠 恢复Claude Pro模式",
                                "清除API配置，恢复默认Claude Pro模式")
        
        try:
            # 清除所有API配置，恢复默认Claude Pro模式
            env_vars_to_clear = ['ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY']
            cleared_vars = []
            
            # 清除运行时环境变量
            for var in env_vars_to_clear:
                if var in os.environ:
                    del os.environ[var]
                    cleared_vars.append(var)
            
            # 持久化到.env文件
            clear_config = {var: "" for var in env_vars_to_clear}
            self._update_env_file(clear_config, clear=True)
            
            print("✅ Claude Pro模式已恢复")
            if cleared_vars:
                print(f"🗑️  已清除环境变量: {', '.join(cleared_vars)}")
            else:
                print("💡 已经在Claude Pro模式下")
            
            self.log_action("恢复Claude Pro模式", f"清除变量: {cleared_vars}")
            
            # 重新启动提示
            print("\n⚠️  重要提示:")
            print("   • 需要重启终端或运行 'source .env' 使配置生效")
            print("   • WSL用户建议运行生成的环境变量脚本")
            
            return "Claude Pro模式已恢复"
            
        except Exception as e:
            self.handle_error(e, "恢复Claude Pro模式")
            return None
    
    def _switch_to_qwen_engine(self) -> Optional[str]:
        """切换到千问3-code引擎"""
        self.display_menu_header("🔄 切换到千问3-code引擎",
                                "配置阿里云千问API作为备用引擎")
        
        print("📋 千问3-code引擎配置:")
        print("   • 供应商: 阿里云")
        print("   • 模型: qwen3-code (1万亿参数MoE)")
        print("   • 特点: 代码生成能力强，中文友好")
        print("   • 费用: 按使用量付费")
        
        # 检查是否已有配置
        existing_key = os.getenv('QWEN_API_KEY', '')
        if not existing_key:
            print("\n⚠️  需要先配置QWEN_API_KEY")
            api_key = input("请输入阿里云千问API密钥 (留空取消): ").strip()
            if not api_key:
                self.display_operation_cancelled()
                return None
        else:
            print(f"\n✅ 检测到已配置的API密钥: {existing_key[:8]}...")
            if not self.confirm_operation("是否使用现有配置？"):
                api_key = input("请输入新的阿里云千问API密钥: ").strip()
                if not api_key:
                    self.display_operation_cancelled()
                    return None
            else:
                api_key = existing_key
        
        try:
            # 配置千问引擎环境变量
            env_config = {
                'ANTHROPIC_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
                'ANTHROPIC_API_KEY': api_key,
                'QWEN_API_KEY': api_key  # 备份保存
            }
            
            # 更新运行时环境变量
            for key, value in env_config.items():
                os.environ[key] = value
            
            # 持久化到.env文件
            self._update_env_file(env_config)
            
            self.display_success_message("千问3-code引擎配置完成")
            self.log_action("切换到千问3-code引擎", "配置完成")
            
            print("🎯 配置详情:")
            print(f"   • Base URL: {env_config['ANTHROPIC_BASE_URL']}")
            print(f"   • API Key: {api_key[:8]}...{api_key[-4:]}")
            
            return "千问3-code引擎已配置"
            
        except Exception as e:
            self.handle_error(e, "切换到千问3-code引擎")
            return None
    
    def _switch_to_kimi_engine(self) -> Optional[str]:
        """切换到Kimi K2引擎"""
        self.display_menu_header("🌙 切换到Kimi K2引擎",
                                "配置月之暗面Kimi API作为备用引擎")
        
        print("📋 Kimi K2引擎配置:")
        print("   • 供应商: 月之暗面 (Moonshot)")
        print("   • 模型: kimi-k2 (1万亿参数MoE)")
        print("   • 特点: 128K上下文，高性价比")
        print("   • 费用: 按使用量付费")
        
        # 检查是否已有配置
        existing_key = os.getenv('MOONSHOT_API_KEY', '')
        if not existing_key:
            print("\n⚠️  需要先配置MOONSHOT_API_KEY")
            api_key = input("请输入月之暗面API密钥 (留空取消): ").strip()
            if not api_key:
                self.display_operation_cancelled()
                return None
        else:
            print(f"\n✅ 检测到已配置的API密钥: {existing_key[:8]}...")
            if not self.confirm_operation("是否使用现有配置？"):
                api_key = input("请输入新的月之暗面API密钥: ").strip()
                if not api_key:
                    self.display_operation_cancelled()
                    return None
            else:
                api_key = existing_key
        
        try:
            # 配置Kimi引擎环境变量
            env_config = {
                'ANTHROPIC_BASE_URL': 'https://api.moonshot.cn/v1',
                'ANTHROPIC_API_KEY': api_key,
                'MOONSHOT_API_KEY': api_key  # 备份保存
            }
            
            # 更新运行时环境变量
            for key, value in env_config.items():
                os.environ[key] = value
            
            # 持久化到.env文件
            self._update_env_file(env_config)
            
            self.display_success_message("Kimi K2引擎配置完成")
            self.log_action("切换到Kimi K2引擎", "配置完成")
            
            print("🎯 配置详情:")
            print(f"   • Base URL: {env_config['ANTHROPIC_BASE_URL']}")
            print(f"   • API Key: {api_key[:8]}...{api_key[-4:]}")
            
            return "Kimi K2引擎已配置"
            
        except Exception as e:
            self.handle_error(e, "切换到Kimi K2引擎")
            return None
    
    def _show_engine_config_details(self) -> Optional[str]:
        """显示引擎配置详情"""
        self.display_menu_header("📋 引擎配置详情",
                                "查看当前所有引擎相关配置")
        
        print("🔍 环境变量配置:")
        env_vars = [
            ('ANTHROPIC_BASE_URL', 'Anthropic API Base URL'),
            ('ANTHROPIC_API_KEY', 'Anthropic API Key'),
            ('ANTHROPIC_AUTH_TOKEN', 'Anthropic Auth Token'),
            ('QWEN_API_KEY', '阿里云千问API密钥'),
            ('MOONSHOT_API_KEY', '月之暗面API密钥')
        ]
        
        for var_name, description in env_vars:
            value = os.getenv(var_name, '')
            if value:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else value
                print(f"   ✅ {description}: {masked_value}")
            else:
                print(f"   ❌ {description}: 未配置")
        
        print("\n📂 配置文件检查:")
        config_files = ['.env', '.env.local', '.env.example']
        for config_file in config_files:
            file_path = Path(config_file)
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"   ✅ {config_file}: {file_size} bytes")
            else:
                print(f"   ❌ {config_file}: 不存在")
        
        # 显示当前引擎状态
        status_info = self._get_current_engine_status()
        print(f"\n📊 当前引擎状态:")
        print(f"   • 引擎: {status_info['engine']}")
        print(f"   • 状态: {status_info['status']}")
        print(f"   • 模型: {status_info['model_info']}")
        
        self.pause_for_user()
        return None
    
    def _test_current_engine_connection(self) -> Optional[str]:
        """测试当前引擎连接"""
        self.display_menu_header("🧪 测试当前引擎连接",
                                "验证当前配置的引擎是否可用")
        
        print("功能开发中...")
        print("💡 该功能将集成实际的API连接测试")
        self.pause_for_user()
        return None
    
    def _reset_engine_config(self) -> Optional[str]:
        """重置引擎配置"""
        self.display_menu_header("🔧 重置引擎配置",
                                "清除所有引擎配置，恢复初始状态")
        
        if not self.confirm_operation("⚠️  这将清除所有LLM引擎配置，确认继续？"):
            self.display_operation_cancelled()
            return None
        
        try:
            # 清除所有相关环境变量
            env_vars_to_clear = [
                'ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY',
                'QWEN_API_KEY', 'MOONSHOT_API_KEY'
            ]
            
            cleared_vars = []
            for var in env_vars_to_clear:
                if var in os.environ:
                    del os.environ[var]
                    cleared_vars.append(var)
            
            # 持久化到.env文件
            clear_config = {var: "" for var in env_vars_to_clear}
            self._update_env_file(clear_config, clear=True)
            
            self.display_success_message("引擎配置已重置")
            print(f"🗑️  已清除 {len(cleared_vars)} 个环境变量")
            self.log_action("重置引擎配置", f"清除变量: {cleared_vars}")
            
            return "引擎配置已重置"
            
        except Exception as e:
            self.handle_error(e, "重置引擎配置")
            return None
    
    def _generate_wsl_env_script(self) -> Optional[str]:
        """生成WSL环境变量设置脚本"""
        self.display_menu_header("📝 生成WSL环境变量设置脚本",
                                "创建用于WSL的环境变量导出脚本")
        
        try:
            script_content = self._create_wsl_export_script()
            
            script_path = Path("set_claude_env.sh")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 设置执行权限
            import stat
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            self.display_success_message(f"WSL环境脚本已生成: {script_path}")
            print("📝 使用方法:")
            print(f"   1. source {script_path}")
            print(f"   2. 或者: chmod +x {script_path} && ./{script_path}")
            
            self.log_action("生成WSL环境变量脚本", str(script_path))
            return str(script_path)
            
        except Exception as e:
            self.handle_error(e, "生成WSL环境变量脚本")
            return None
    
    def _update_env_file(self, env_config: Dict[str, str], clear: bool = False):
        """更新.env文件"""
        env_file = Path(".env")
        
        if clear and env_config:
            # 清除指定的环境变量
            if env_file.exists():
                lines = env_file.read_text(encoding='utf-8').splitlines()
                new_lines = []
                for line in lines:
                    if '=' in line:
                        key = line.split('=')[0]
                        if key not in env_config:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                env_file.write_text('\\n'.join(new_lines) + '\\n', encoding='utf-8')
        elif env_config:
            # 更新环境变量
            existing_lines = []
            if env_file.exists():
                existing_lines = env_file.read_text(encoding='utf-8').splitlines()
            
            # 创建新的行列表
            new_lines = []
            updated_keys = set()
            
            # 更新现有行
            for line in existing_lines:
                if '=' in line:
                    key = line.split('=')[0]
                    if key in env_config:
                        new_lines.append(f"{key}={env_config[key]}")
                        updated_keys.add(key)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # 添加新的配置项
            for key, value in env_config.items():
                if key not in updated_keys:
                    new_lines.append(f"{key}={value}")
            
            env_file.write_text('\\n'.join(new_lines) + '\\n', encoding='utf-8')
    
    def _create_wsl_export_script(self) -> str:
        """创建WSL导出脚本内容"""
        current_time = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        script_content = f"""#!/bin/bash
# WSL环境变量设置脚本
# 生成时间: {current_time}
# 用法: source set_claude_env.sh

echo "🔧 设置Claude LLM引擎环境变量..."

# 检查当前配置
"""
        
        # 添加当前环境变量配置
        env_vars = ['ANTHROPIC_BASE_URL', 'ANTHROPIC_API_KEY', 'QWEN_API_KEY', 'MOONSHOT_API_KEY']
        for var in env_vars:
            value = os.getenv(var, '')
            if value:
                script_content += f'export {var}="{value}"\\n'
                script_content += f'echo "✅ 已设置 {var}"\\n'
        
        script_content += """
echo "🎯 环境变量设置完成"
echo "💡 可运行 'env | grep ANTHROPIC' 查看配置"
"""
        
        return script_content
    
    def handle_audio_tools_menu(self) -> None:
        """语音和音频工具菜单 (合并原功能12+相关)"""
        menu_title = "🔊 语音和音频工具"
        menu_description = "🎙️ TTS服务管理和音频处理工具"
        
        options = [
            "1. TTS语音测试",
            "2. 音频质量评估", 
            "3. 语音服务切换",
            "4. 音频格式转换"
        ]
        
        handlers = [
            self._tts_voice_test,
            self._audio_quality_assessment,
            self._voice_service_switch,
            self._audio_format_conversion
        ]
        
        self.create_menu_loop(menu_title, menu_description, options, handlers)
    
    def _tts_voice_test(self) -> Optional[str]:
        """TTS语音测试 (原ElevenLabs测试)"""
        print("\n🎙️ TTS语音测试")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _audio_quality_assessment(self) -> Optional[str]:
        """音频质量评估"""
        print("\n📊 音频质量评估")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _voice_service_switch(self) -> Optional[str]:
        """语音服务切换"""
        print("\n🔄 语音服务切换")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _audio_format_conversion(self) -> Optional[str]:
        """音频格式转换"""
        print("\n🔊 音频格式转换")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def handle_system_tools_menu(self) -> None:
        """系统工具集合菜单 (合并原功能7+10+11)"""
        menu_title = "⚙️ 系统工具集合"
        menu_description = "🛠️ 系统维护和配置管理"
        
        options = [
            "1. 系统状态检查",
            "2. LLM引擎切换",
            "3. 调试和维护",
            "4. 配置管理",
            "5. 日志查看"
        ]
        
        handlers = [
            self._system_status_check,
            self._llm_engine_switch,
            self._debug_maintenance,
            self._config_management,
            self._log_viewer
        ]
        
        self.create_menu_loop(menu_title, menu_description, options, handlers)
    
    def _system_status_check(self) -> Optional[str]:
        """系统状态检查 (原功能7)"""
        print("\n🔍 系统状态检查")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _llm_engine_switch(self) -> Optional[str]:
        """LLM引擎切换 (原功能10)"""
        return self.handle_llm_engine_menu()
    
    def _debug_maintenance(self) -> Optional[str]:
        """调试和维护 (原功能11)"""
        print("\n🔧 调试和维护")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _config_management(self) -> Optional[str]:
        """配置管理"""
        print("\n⚙️ 配置管理")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _log_viewer(self) -> Optional[str]:
        """日志查看"""
        print("\n📋 日志查看")
        print("(功能开发中...)")
        self.pause_for_user()
        return None