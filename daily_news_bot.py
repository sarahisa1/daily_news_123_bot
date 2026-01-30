#!/usr/bin/env python3
"""
📊 일일 경제 뉴스 TOP10 텔레그램 봇 (GitHub Actions 버전)
매일 자동으로 경제/주식/해외주식/원자재/암호화폐 뉴스를 발송합니다.

GitHub Actions에서 실행되며, 환경변수로 설정을 받습니다.
"""

import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
import telegram
from telegram.constants import ParseMode
import logging
import os
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경변수에서 설정 읽기
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')


class NewsCollector:
    """뉴스 수집 클래스"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    
    async def fetch_page(self, session, url):
        """웹 페이지 가져오기"""
        try:
            async with session.get(url, headers=self.headers, timeout=15) as response:
                return await response.text()
        except Exception as e:
            logger.error(f"페이지 로드 실패: {url} - {e}")
            return None

    async def get_naver_economy_news(self, session):
        """네이버 경제 뉴스 TOP10"""
        url = "https://news.naver.com/section/101"
        news_list = []
        
        try:
            html = await self.fetch_page(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                headlines = soup.select('.sa_text_title')[:10]
                for idx, item in enumerate(headlines, 1):
                    title = item.get_text(strip=True)
                    link = item.get('href', '')
                    if title and link:
                        news_list.append({
                            'rank': idx,
                            'title': title[:60] + '...' if len(title) > 60 else title,
                            'link': link
                        })
        except Exception as e:
            logger.error(f"네이버 경제 뉴스 수집 실패: {e}")
        
        return news_list

    async def get_stock_news(self, session):
        """국내 주식 뉴스 TOP10"""
        url = "https://finance.naver.com/news/mainnews.naver"
        news_list = []
        
        try:
            html = await self.fetch_page(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('.articleSubject a')[:10]
                for idx, item in enumerate(items, 1):
                    title = item.get_text(strip=True)
                    link = "https://finance.naver.com" + item.get('href', '')
                    if title:
                        news_list.append({
                            'rank': idx,
                            'title': title[:60] + '...' if len(title) > 60 else title,
                            'link': link
                        })
        except Exception as e:
            logger.error(f"국내 주식 뉴스 수집 실패: {e}")
        
        return news_list

    async def get_world_stock_news(self, session):
        """해외 주식 뉴스 TOP10"""
        url = "https://finance.naver.com/world/"
        news_list = []
        
        try:
            html = await self.fetch_page(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('.news_list li a')[:10]
                for idx, item in enumerate(items, 1):
                    title = item.get_text(strip=True)
                    link = item.get('href', '')
                    if not link.startswith('http'):
                        link = "https://finance.naver.com" + link
                    if title:
                        news_list.append({
                            'rank': idx,
                            'title': title[:60] + '...' if len(title) > 60 else title,
                            'link': link
                        })
        except Exception as e:
            logger.error(f"해외 주식 뉴스 수집 실패: {e}")
        
        return news_list

    async def get_commodity_news(self, session):
        """원자재 뉴스 TOP10"""
        url = "https://search.naver.com/search.naver?where=news&query=원자재+금+유가+시세"
        news_list = []
        
        try:
            html = await self.fetch_page(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('.news_tit')[:10]
                for idx, item in enumerate(items, 1):
                    title = item.get_text(strip=True)
                    link = item.get('href', '')
                    if title:
                        news_list.append({
                            'rank': idx,
                            'title': title[:60] + '...' if len(title) > 60 else title,
                            'link': link
                        })
        except Exception as e:
            logger.error(f"원자재 뉴스 수집 실패: {e}")
        
        return news_list

    async def get_crypto_news(self, session):
        """암호화폐 뉴스 TOP10"""
        url = "https://search.naver.com/search.naver?where=news&query=비트코인+암호화폐+이더리움"
        news_list = []
        
        try:
            html = await self.fetch_page(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('.news_tit')[:10]
                for idx, item in enumerate(items, 1):
                    title = item.get_text(strip=True)
                    link = item.get('href', '')
                    if title:
                        news_list.append({
                            'rank': idx,
                            'title': title[:60] + '...' if len(title) > 60 else title,
                            'link': link
                        })
        except Exception as e:
            logger.error(f"암호화폐 뉴스 수집 실패: {e}")
        
        return news_list

    async def get_market_indices(self, session):
        """주요 시장 지수 가져오기"""
        indices = {}
        
        # 국내 지수
        url = "https://finance.naver.com/sise/"
        try:
            html = await self.fetch_page(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                kospi = soup.select_one('#KOSPI_now')
                if kospi:
                    indices['KOSPI'] = kospi.get_text(strip=True)
                kosdaq = soup.select_one('#KOSDAQ_now')
                if kosdaq:
                    indices['KOSDAQ'] = kosdaq.get_text(strip=True)
        except Exception as e:
            logger.error(f"국내 지수 수집 실패: {e}")
        
        # 해외 지수
        world_url = "https://finance.naver.com/world/"
        try:
            html = await self.fetch_page(session, world_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                world_indices = soup.select('.data_lst tr')
                for row in world_indices[:5]:
                    name_elem = row.select_one('.name')
                    value_elem = row.select_one('.point')
                    if name_elem and value_elem:
                        name = name_elem.get_text(strip=True)
                        value = value_elem.get_text(strip=True)
                        indices[name] = value
        except Exception as e:
            logger.error(f"해외 지수 수집 실패: {e}")
        
        return indices

    async def collect_all_news(self):
        """모든 뉴스 수집"""
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                self.get_naver_economy_news(session),
                self.get_stock_news(session),
                self.get_world_stock_news(session),
                self.get_commodity_news(session),
                self.get_crypto_news(session),
                self.get_market_indices(session),
                return_exceptions=True
            )
            
            return {
                'economy': results[0] if not isinstance(results[0], Exception) else [],
                'stock': results[1] if not isinstance(results[1], Exception) else [],
                'world_stock': results[2] if not isinstance(results[2], Exception) else [],
                'commodity': results[3] if not isinstance(results[3], Exception) else [],
                'crypto': results[4] if not isinstance(results[4], Exception) else [],
                'indices': results[5] if not isinstance(results[5], Exception) else {}
            }


class TelegramNewsBot:
    """텔레그램 뉴스 봇"""
    
    def __init__(self, token, chat_id):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.collector = NewsCollector()
    
    def format_news_message(self, news_data):
        """뉴스 메시지 포맷팅"""
        today = datetime.now().strftime('%Y년 %m월 %d일 (%a)')
        
        message = f"""
📰 <b>일일 경제 뉴스 TOP10</b>
📅 {today}

━━━━━━━━━━━━━━━━━━━━━━

"""
        # 시장 지수
        if news_data.get('indices'):
            message += "📊 <b>주요 시장 지수</b>\n"
            for name, value in news_data['indices'].items():
                message += f"  • {name}: {value}\n"
            message += "\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 각 카테고리별 뉴스
        categories = [
            ('economy', '💰 경제 뉴스 TOP5'),
            ('stock', '📈 국내 주식 뉴스 TOP5'),
            ('world_stock', '🌍 해외 주식 뉴스 TOP5'),
            ('commodity', '🛢️ 원자재 뉴스 TOP5'),
            ('crypto', '₿ 암호화폐 뉴스 TOP5'),
        ]
        
        for key, title in categories:
            news_list = news_data.get(key, [])
            if news_list:
                message += f"<b>{title}</b>\n\n"
                for news in news_list[:5]:
                    message += f"{news['rank']}. {news['title']}\n"
                message += "\n"
        
        message += """━━━━━━━━━━━━━━━━━━━━━━
🤖 Powered by GitHub Actions
"""
        return message

    def format_detailed_message(self, news_data, category, title):
        """카테고리별 상세 메시지 (링크 포함)"""
        news_list = news_data.get(category, [])
        if not news_list:
            return None
        
        message = f"<b>{title}</b>\n\n"
        for news in news_list[:10]:
            message += f"{news['rank']}. <a href='{news['link']}'>{news['title']}</a>\n\n"
        
        return message

    async def send_news(self):
        """뉴스 발송"""
        logger.info("뉴스 수집 시작...")
        news_data = await self.collector.collect_all_news()
        
        # 요약 메시지 발송
        summary_message = self.format_news_message(news_data)
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=summary_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            logger.info("✅ 요약 뉴스 발송 완료")
        except Exception as e:
            logger.error(f"❌ 요약 메시지 발송 실패: {e}")
            raise
        
        # 카테고리별 상세 메시지 발송
        categories = [
            ('economy', '💰 경제 뉴스 상세'),
            ('stock', '📈 국내 주식 뉴스 상세'),
            ('world_stock', '🌍 해외 주식 뉴스 상세'),
            ('commodity', '🛢️ 원자재 뉴스 상세'),
            ('crypto', '₿ 암호화폐 뉴스 상세'),
        ]
        
        for key, title in categories:
            detailed_msg = self.format_detailed_message(news_data, key, title)
            if detailed_msg:
                try:
                    await asyncio.sleep(1)  # rate limit 방지
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=detailed_msg,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    logger.info(f"✅ {title} 발송 완료")
                except Exception as e:
                    logger.error(f"❌ {title} 발송 실패: {e}")
        
        logger.info("🎉 모든 뉴스 발송 완료!")


async def main():
    """메인 함수"""
    # 환경변수 확인
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    if not CHAT_ID:
        logger.error("❌ CHAT_ID 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    logger.info(f"🚀 봇 시작 - Chat ID: {CHAT_ID[:4]}***")
    
    bot = TelegramNewsBot(BOT_TOKEN, CHAT_ID)
    await bot.send_news()


if __name__ == "__main__":
    asyncio.run(main())
