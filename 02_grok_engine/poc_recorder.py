#!/usr/bin/env python3
"""
Bounty PoC Video Recorder
Records browser video showing data exfiltration for bug bounty submissions.
Usage: python poc-recorder.py --url "https://target.com" --payload "javascript:..." --output poc_video.webm
"""
import argparse
import asyncio
import json
import sys
import os
from datetime import datetime

async def record_poc(url, payload_url=None, actions=None, output="poc_video", wait_time=5, headless=False):
    from playwright.async_api import async_playwright
    
    video_path = f"{output}.webm"
    har_path = f"{output}.har"
    screenshot_path = f"{output}.png"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=".",
            record_video_size={"width": 1280, "height": 720}
        )
        
        # Start HAR recording for network evidence
        await context.tracing.start(screenshots=True, sources=True)
        
        page = await context.new_page()
        
        print(f"[*] Navigating to: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # If payload URL provided (XSS/injection)
        if payload_url:
            print(f"[*] Executing payload: {payload_url[:80]}...")
            await page.goto(payload_url, timeout=15000)
            await page.wait_for_timeout(wait_time * 1000)
        
        # If custom actions provided
        if actions:
            for action in actions:
                action_type = action.get("type", "")
                if action_type == "click":
                    print(f"[*] Clicking: {action['selector']}")
                    await page.click(action["selector"])
                    await page.wait_for_timeout(action.get("wait", 1000))
                elif action_type == "type":
                    print(f"[*] Typing into: {action['selector']}")
                    await page.fill(action["selector"], action["text"])
                    await page.wait_for_timeout(action.get("wait", 500))
                elif action_type == "wait":
                    print(f"[*] Waiting {action['ms']}ms...")
                    await page.wait_for_timeout(action["ms"])
                elif action_type == "navigate":
                    print(f"[*] Navigating to: {action['url']}")
                    await page.goto(action["url"], timeout=15000)
                    await page.wait_for_timeout(action.get("wait", 3000))
                elif action_type == "evaluate":
                    print(f"[*] Running JS...")
                    result = await page.evaluate(action["script"])
                    if result:
                        print(f"[+] Result: {json.dumps(result, indent=2)[:500]}")
                    await page.wait_for_timeout(action.get("wait", 1000))
                elif action_type == "screenshot":
                    await page.screenshot(path=action.get("path", screenshot_path))
                    print(f"[*] Screenshot saved: {action.get('path', screenshot_path)}")
        
        # Final screenshot
        await page.screenshot(path=screenshot_path)
        print(f"[*] Final screenshot: {screenshot_path}")
        
        # Get page content as evidence
        content = await page.content()
        with open(f"{output}_page.html", "w") as f:
            f.write(content)
        print(f"[*] Page HTML saved: {output}_page.html")
        
        # Additional wait to capture exfiltration
        print(f"[*] Waiting {wait_time}s to capture data exfiltration...")
        await page.wait_for_timeout(wait_time * 1000)
        
        # Save trace
        await context.tracing.stop(path=f"{output}_trace.zip")
        print(f"[*] Network trace saved: {output}_trace.zip")
        
        await context.close()
        await browser.close()
        
        # Move video from temp dir
        video_file = None
        for f in os.listdir("."):
            if f.endswith(".webm") and output not in f:
                os.rename(f, video_path)
                video_file = video_path
                break
        
        if not video_file and os.path.exists(video_path):
            video_file = video_path
        
        print(f"\n[+] DONE! Files saved:")
        if video_file:
            print(f"    Video:  {video_file}")
        print(f"    Screenshot: {screenshot_path}")
        print(f"    Trace:  {output}_trace.zip")
        print(f"    HTML:   {output}_page.html")
        
        return video_file

def main():
    parser = argparse.ArgumentParser(description="Bounty PoC Video Recorder")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--payload", help="Payload URL (XSS, redirect, etc.)")
    parser.add_argument("--output", default=f"poc_{datetime.now().strftime('%Y%m%d_%H%M%S')}", help="Output filename prefix")
    parser.add_argument("--wait", type=int, default=5, help="Wait time after payload (seconds)")
    parser.add_argument("--headless", action="store_true", help="Run headless (no browser window)")
    parser.add_argument("--actions", help="JSON file with custom actions")
    
    args = parser.parse_args()
    
    actions = None
    if args.actions:
        with open(args.actions) as f:
            actions = json.load(f)
    
    asyncio.run(record_poc(
        url=args.url,
        payload_url=args.payload,
        actions=actions,
        output=args.output,
        wait_time=args.wait,
        headless=args.headless
    ))

if __name__ == "__main__":
    main()