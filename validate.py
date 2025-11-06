#!/usr/bin/env python3
"""
Validation script for TextExpense site reorganization
Tests file structure, links, and critical functionality
"""

import os
import re
from pathlib import Path
from html.parser import HTMLParser

class LinkExtractor(HTMLParser):
    """Extract links from HTML"""
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])
        if tag == 'img' and 'src' in attrs_dict:
            self.images.append(attrs_dict['src'])
        if tag == 'link' and 'href' in attrs_dict:
            self.images.append(attrs_dict['href'])

def check_file_exists(filepath):
    """Check if file exists"""
    return os.path.exists(filepath)

def check_placeholders(filepath):
    """Check for unreplaced template placeholders"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        placeholders = re.findall(r'\{\{[^}]+\}\}', content)
        return placeholders

def validate_links_in_file(filepath, base_dir):
    """Validate all links in an HTML file"""
    issues = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = LinkExtractor()
    try:
        parser.feed(content)
    except:
        issues.append(f"  ❌ HTML parsing error in {filepath}")
        return issues

    file_dir = os.path.dirname(filepath)

    # Check all links
    for link in parser.links:
        # Skip external links and anchors
        if link.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'wa.me')):
            continue

        # Resolve relative path
        if link.startswith('../'):
            target = os.path.normpath(os.path.join(file_dir, link))
        elif link.startswith('./'):
            target = os.path.normpath(os.path.join(file_dir, link[2:]))
        else:
            target = os.path.normpath(os.path.join(file_dir, link))

        if not os.path.exists(target):
            issues.append(f"  ❌ Broken link: {link} -> {target}")

    # Check all images
    for img in parser.images:
        # Skip external images and data URIs
        if img.startswith(('http://', 'https://', 'data:')):
            continue

        # Resolve relative path
        if img.startswith('../'):
            target = os.path.normpath(os.path.join(file_dir, img))
        elif img.startswith('./'):
            target = os.path.normpath(os.path.join(file_dir, img[2:]))
        else:
            target = os.path.normpath(os.path.join(file_dir, img))

        if not os.path.exists(target):
            issues.append(f"  ❌ Missing image: {img} -> {target}")

    return issues

def check_whatsapp_urls(filepath):
    """Check for duplicate query parameters in WhatsApp URLs"""
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all WhatsApp URLs
    wa_urls = re.findall(r'wa\.me/[^"\'>\s]+', content)

    for url in wa_urls:
        # Check for duplicate ?text= parameters
        if url.count('?text=') > 1:
            issues.append(f"  ⚠️  Duplicate query params: {url}")

    return issues

def main():
    print("=" * 70)
    print("🔍 TEXTEXPENSE VALIDATION REPORT")
    print("=" * 70)
    print()

    base_dir = os.getcwd()
    total_issues = 0

    # Test 1: File Structure
    print("📁 TEST 1: File Structure")
    print("-" * 70)

    required_files = {
        'index.html': 'Main landing page',
        'assets/te-logo.png': 'Logo file',
        'pages/index.html': 'Solutions hub page',
        'pages/tax-receipts.html': 'Tax receipts landing page',
        'pages/expense-reimbursement.html': 'Expense reimbursement page',
        'pages/small-business-accounting.html': 'Small business page',
        'pages/warranty-returns.html': 'Warranty returns page',
        'blog/index.html': 'Blog hub page',
        '_landing-template.html': 'Landing page template',
        '_blog-template.html': 'Blog post template',
        'DEPLOYMENT.md': 'Deployment documentation'
    }

    for filepath, description in required_files.items():
        if check_file_exists(filepath):
            print(f"  ✅ {filepath} - {description}")
        else:
            print(f"  ❌ {filepath} - MISSING")
            total_issues += 1

    print()

    # Test 2: Template Placeholders
    print("🔖 TEST 2: Template Placeholders")
    print("-" * 70)

    production_files = [
        'index.html',
        'pages/index.html',
        'pages/tax-receipts.html',
        'pages/expense-reimbursement.html',
        'pages/small-business-accounting.html',
        'pages/warranty-returns.html',
        'blog/index.html'
    ]

    placeholder_issues = 0
    for filepath in production_files:
        if os.path.exists(filepath):
            placeholders = check_placeholders(filepath)
            if placeholders:
                print(f"  ❌ {filepath}: Found {len(placeholders)} placeholders")
                for p in placeholders[:3]:  # Show first 3
                    print(f"      - {p}")
                placeholder_issues += len(placeholders)
            else:
                print(f"  ✅ {filepath}: No placeholders")

    if placeholder_issues > 0:
        total_issues += placeholder_issues

    print()

    # Test 3: Link Validation
    print("🔗 TEST 3: Link Validation")
    print("-" * 70)

    link_issues = 0
    for filepath in production_files:
        if os.path.exists(filepath):
            issues = validate_links_in_file(filepath, base_dir)
            if issues:
                print(f"  ❌ {filepath}:")
                for issue in issues:
                    print(issue)
                    link_issues += 1
            else:
                print(f"  ✅ {filepath}: All links valid")

    if link_issues > 0:
        total_issues += link_issues

    print()

    # Test 4: WhatsApp URLs
    print("📱 TEST 4: WhatsApp URLs")
    print("-" * 70)

    wa_issues = 0
    for filepath in production_files:
        if os.path.exists(filepath):
            issues = check_whatsapp_urls(filepath)
            if issues:
                print(f"  ❌ {filepath}:")
                for issue in issues:
                    print(issue)
                    wa_issues += 1
            else:
                # Count WhatsApp links
                with open(filepath, 'r') as f:
                    wa_count = f.read().count('wa.me/')
                print(f"  ✅ {filepath}: {wa_count} WhatsApp links, all clean")

    if wa_issues > 0:
        total_issues += wa_issues

    print()

    # Test 5: Critical Path Checks
    print("🛣️  TEST 5: Critical Path Checks")
    print("-" * 70)

    path_tests = [
        ('index.html', './assets/te-logo.png', 'Main site -> Logo'),
        ('index.html', './pages/tax-receipts.html', 'Main site -> Tax receipts'),
        ('pages/tax-receipts.html', '../assets/te-logo.png', 'Page -> Logo'),
        ('pages/tax-receipts.html', '../index.html', 'Page -> Main site'),
        ('pages/index.html', './tax-receipts.html', 'Hub -> Tax receipts'),
        ('blog/index.html', '../assets/te-logo.png', 'Blog -> Logo'),
    ]

    path_issues = 0
    for source_file, expected_path, description in path_tests:
        if not os.path.exists(source_file):
            print(f"  ⚠️  {description}: Source file missing")
            continue

        with open(source_file, 'r') as f:
            content = f.read()

        if expected_path in content:
            print(f"  ✅ {description}: Found '{expected_path}'")
        else:
            print(f"  ❌ {description}: Missing '{expected_path}'")
            path_issues += 1

    if path_issues > 0:
        total_issues += path_issues

    print()

    # Test 6: File Sizes (sanity check)
    print("📊 TEST 6: File Size Check")
    print("-" * 70)

    for filepath in production_files:
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            if size_kb > 100:
                print(f"  ⚠️  {filepath}: {size_kb:.1f} KB (large)")
            elif size_kb < 1:
                print(f"  ⚠️  {filepath}: {size_kb:.1f} KB (suspiciously small)")
            else:
                print(f"  ✅ {filepath}: {size_kb:.1f} KB")

    print()

    # Final Summary
    print("=" * 70)
    print("📋 VALIDATION SUMMARY")
    print("=" * 70)

    if total_issues == 0:
        print("✅ ALL TESTS PASSED! Safe to merge.")
    else:
        print(f"❌ FOUND {total_issues} ISSUE(S). Review before merging.")

    print()
    print("Next steps:")
    print("  1. Review any issues above")
    print("  2. Test visually in browser: python3 -m http.server 8080")
    print("  3. Open http://localhost:8080 and click through pages")
    print("  4. Test mobile view (resize browser < 768px)")
    print()

    return total_issues

if __name__ == '__main__':
    exit_code = main()
    exit(0 if exit_code == 0 else 1)
