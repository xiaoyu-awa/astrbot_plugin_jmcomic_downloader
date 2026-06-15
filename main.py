from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from pathlib import Path
from jmcomic import *

import astrbot.api.message_components as Comp
import asyncio
import jmcomic



@register("jmcomic", "筱雨awa", "禁漫下载器", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        self.client = JmOption.default().new_jm_client()
        self.plugin_data_path = Path(get_astrbot_data_path()) / "plugins" / self.name
        self.option = create_option_by_file(str(self.plugin_data_path / 'jmcomic.yml'))



    async def terminate(self):
        """结束运行"""

    @filter.command("jm")
    async def jmcomic(self, event: AstrMessageEvent):
        """下载禁漫本子"""
        message_str = event.message_str
        args = message_str.split()
        if len(args) != 2:
            yield event.plain_result("下载本子用法: /jm [id]")
            return
        album_id = args[1]


        text = self.get_info(album_id)
        yield event.plain_result(text)
        yield event.plain_result("正在下载，等一下喵w")


        await jmcomic.download_album_async(album_id, option=self.option,
                                                 extra=Feature.export_pdf(
                                                    # 下面是自定义参数
                                                    pdf_dir=str(self.plugin_data_path / "tmp"),          # PDF 保存到 D:/my_pdfs 文件夹
                                                    filename_rule=album_id,        # 用本子标题作为文件名
                                                    delete_original_file=True,     # 合并完 PDF 后删除原图
                                                ))

        file = Comp.File(file=str(self.plugin_data_path / "tmp" / (album_id + ".pdf")), name="jm" + album_id + ".pdf")
        yield event.chain_result([file])


    @filter.command("jmv")
    async def jmcomicview(self, event: AstrMessageEvent):
        """查询禁漫本子"""
        message_str = event.message_str
        args = message_str.split()
        if len(args) != 2:
            yield event.plain_result("查询本子用法: /jmv [id]")
            return
        album_id = args[1]
        

        text = self.get_info(album_id)
        yield event.plain_result(text)

    
    def _truncate_list(self, items, limit=10):
        if len(items) <= limit:
            return ', '.join(items)
        return ', '.join(items[:limit]) + f' ...等{len(items)}个'
    
    def get_info(self, ambum_id):
        # 捕获获取本子/章节详情时可能出现的异常
        try:
            # 请求本子实体类
            album: JmAlbumDetail = self.client.get_album_detail(ambum_id)
        except MissingAlbumPhotoException as e:
            return(f'id={e.error_jmid}的本子不存在')

        except JsonResolveFailException as e:
            # 响应对象
            resp = e.resp
            return(f'解析json失败\nresp.text: {resp.text}, resp.status_code: {resp.status_code}')

        except RequestRetryAllFailException as e:
            return(f'请求失败，重试次数耗尽')

        except JmcomicException as e:
            # 捕获所有异常，用作兜底
            return(f'jmcomic遇到异常: {e}')
        
        text = f"""─────
📖 标题:  {album.name}
🆔 ID:    JM{album.album_id}
🔗 链接:  {JmcomicText.format_album_url(album.album_id)}
🎨 封面:  {JmcomicText.get_album_cover_url(album.album_id)}
✍️ 作者:  {self._truncate_list(album.authors) if album.authors else "未知"}
─────
👀 观看:      {album.views}
❤️ 点赞:     {album.likes}
💬 评论:      {album.comment_count}
─────"""

        if album.tags:
            text = text + "\n" + f'🏷️ 标签:  {self._truncate_list(album.tags)}'
        if album.actors:
            text = text + "\n" + f'🎭 人物:  {self._truncate_list(album.actors)}'
        if album.works:
            text = text + "\n" + f'📚 作品:  {self._truncate_list(album.works)}'
        if album.description:
            text = text + "\n" + f'📝 简介:  {album.description}'
        text = text + "\n" + "─────"
        episode_count = len(album.episode_list)
        text = text + "\n" + f'📑 章节 ({episode_count}):'
        i = 0
        for pid, pindex, pname in album.episode_list:
            if i>=10:
                break
            pname = pname.strip()
            text = text + "\n" + f'     第{pindex}話  {pname}  (id: {pid})'
            i=i+1
        text = text + "─────"

        return text