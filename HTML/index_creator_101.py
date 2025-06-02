#!/usr/bin/env python3
#!/usr/bin/env python3
"""
python mhtml_indexer.py /path/to/your/folder

python mhtml_indexer.py /path/to/your/folder --output custom_index.html --title "My MHTML Collection"

For Windows users (no programming required):

Navigate to the main folder in File Explorer
Hold Shift, right-click in the empty space, and select "Open command window here" or "Open PowerShell window here"
Type dir /s /b *.mhtml > index.txt to create a basic text index


    Generate an HTML index of all MHTML files in a directory and its subdirectories.

import os
import argparse
from datetime import datetime

def generate_index(root_dir, output_file='index.html', title='File Index'):
    
    Args:
        root_dir (str): The root directory to start indexing from
        output_file (str): The output HTML file name
        title (str): The title for the index page
    """
  
import os
import argparse
from datetime import datetime

def generate_index(root_dir, output_file='index.html', title='File Index'):
    """
    Generate an HTML index of all MHTML files in a directory and its subdirectories.
    
    Args:
        root_dir (str): The root directory to start indexing from
        output_file (str): The output HTML file name
        title (str): The title for the index page
    """
    # Get all files and folders
    file_structure = {}
    total_files = 0
    
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Get relative path from root directory
        rel_path = os.path.relpath(dirpath, root_dir)
        if rel_path == '.':
            rel_path = ''
            
        # Filter for mhtml files
        mhtml_files = [f for f in filenames if f.lower().endswith('.mhtml')]
        
        if mhtml_files:
            # Store the files with their metadata
            file_structure[rel_path] = []
            for filename in mhtml_files:
                filepath = os.path.join(dirpath, filename)
                file_size = os.path.getsize(filepath)
                mod_time = os.path.getmtime(filepath)
                
                # Create relative file path for the HTML link
                rel_file_path = os.path.join(rel_path, filename) if rel_path else filename
                # Use forward slashes for URLs even on Windows
                rel_file_path = rel_file_path.replace('\\', '/')
                
                file_structure[rel_path].append({
                    'name': filename,
                    'path': rel_file_path,
                    'size': file_size,
                    'modified': datetime.fromtimestamp(mod_time)
                })
                total_files += 1
    
    # Generate HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            border-bottom: 2px solid #ddd;
            padding-bottom: 10px;
        }}
        .folder {{
            margin-bottom: 30px;
        }}
        .folder-name {{
            background-color: #f0f0f0;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
        }}
        .folder-content {{
            margin-left: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        #stats {{
            margin-bottom: 20px;
            color: #666;
        }}
        #search {{
            padding: 8px;
            margin-bottom: 20px;
            width: 100%;
            max-width: 300px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .hidden {{
            display: none;
        }}
        #toc {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            background-color: #f9f9f9;
            max-height: 200px;
            overflow-y: auto;
        }}
        #toc-title {{
            cursor: pointer;
            font-weight: bold;
        }}
        #toc-content {{
            margin-top: 10px;
        }}
        #toc-content a {{
            display: block;
            padding: 3px 0;
            text-decoration: none;
            color: #0366d6;
        }}
        #toc-content a:hover {{
            text-decoration: underline;
        }}
        #back-to-top {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #0366d6;
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            text-align: center;
            line-height: 40px;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div id="stats">
        Total folders: {len(file_structure)} | Total files: {total_files}
    </div>
    
    <input type="text" id="search" placeholder="Search files...">
    
    <div id="toc">
        <div id="toc-title">Table of Contents</div>
        <div id="toc-content">
''')
        
        # Generate Table of Contents
        for folder_path in sorted(file_structure.keys()):
            folder_name = folder_path if folder_path else 'Root'
            folder_id = folder_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            f.write(f'            <a href="#{folder_id}">{folder_name}</a>\n')
            
        f.write('''        </div>
    </div>
''')
        
        # Generate folders and files
        for folder_path in sorted(file_structure.keys()):
            folder_name = folder_path if folder_path else 'Root'
            folder_id = folder_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            
            f.write(f'''    <div class="folder" id="{folder_id}">
        <div class="folder-name" onclick="toggleFolder(this)">{folder_name} ({len(file_structure[folder_path])} files)</div>
        <div class="folder-content">
            <table>
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Size</th>
                        <th>Last Modified</th>
                    </tr>
                </thead>
                <tbody>
''')
            
            # Sort files by name
            for file_info in sorted(file_structure[folder_path], key=lambda x: x['name'].lower()):
                size_str = format_size(file_info['size'])
                date_str = file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')
                
                f.write(f'''                    <tr>
                        <td><a href="{file_info['path']}">{file_info['name']}</a></td>
                        <td>{size_str}</td>
                        <td>{date_str}</td>
                    </tr>
''')
                
            f.write('''                </tbody>
            </table>
        </div>
    </div>
''')
            
        f.write('''    <a href="#" id="back-to-top">↑</a>

    <script>
        function toggleFolder(element) {
            const content = element.nextElementSibling;
            content.classList.toggle('hidden');
        }
        
        // Table of Contents toggle
        document.getElementById('toc-title').addEventListener('click', function() {
            document.getElementById('toc-content').classList.toggle('hidden');
        });
        
        // Search functionality
        document.getElementById('search').addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('table tbody tr');
            
            rows.forEach(row => {
                const filename = row.querySelector('td:first-child').textContent.toLowerCase();
                if (filename.includes(searchTerm)) {
                    row.style.display = '';
                    // Make sure parent folder is visible
                    let folderContent = row.closest('.folder-content');
                    folderContent.classList.remove('hidden');
                    // Make sure parent folder is visible
                    let folder = folderContent.closest('.folder');
                    folder.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Show/hide folders based on whether they have visible files
            const folders = document.querySelectorAll('.folder');
            folders.forEach(folder => {
                const visibleRows = folder.querySelectorAll('tbody tr[style=""]').length;
                const hasSearch = this.value.length > 0;
                
                if (hasSearch && visibleRows === 0) {
                    folder.style.display = 'none';
                } else {
                    folder.style.display = '';
                }
            });
        });
    </script>
</body>
</html>''')

def format_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0 or unit == 'GB':
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an HTML index of MHTML files')
    parser.add_argument('root_dir', help='Root directory to index')
    parser.add_argument('--output', '-o', default='index.html', help='Output HTML file')
    parser.add_argument('--title', '-t', default='MHTML Files Index', help='Page title')
    
    args = parser.parse_args()
    
    print(f"Indexing {args.root_dir}...")
    generate_index(args.root_dir, args.output, args.title)
    print(f"Index generated at {args.output}")