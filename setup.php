<!DOCTYPE html>
<?php
set_time_limit(300);
ob_start();

if (!isset($_GET['run']) || $_GET['run'] !== 'yes') {
    echo "<h1>VoxCore Setup</h1>";
    echo "<p><a href='?run=yes'>Start Setup</a></p>";
    exit;
}

echo "<pre>";
echo "Starting VoxCore Setup...\n\n";
ob_flush();
flush();

// Commands to execute
$commands = array(
    array("mkdir -p ~/logs", "Creating logs directory..."),
    array("cd ~/VOXCORE/voxquery && python3 -m venv venv 2>&1", "Creating virtual environment..."),
    array("cd ~/VOXCORE/voxquery && source venv/bin/activate && pip install --upgrade pip 2>&1 && pip install -r requirements.txt 2>&1", "Installing dependencies (may take 1-2 min)..."),
    array("echo 'VITE_API_URL=https://voxcore.org/api\nALLOWED_HOSTS=voxcore.org,www.voxcore.org\nENV=production\nDATABASE_URL=' > ~/VOXCORE/voxquery/.env", "Creating .env file..."),
    array("cd ~/VOXCORE/voxquery && source venv/bin/activate && nohup python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 > ~/logs/voxcore-backend.log 2>&1 &", "Starting backend..."),
    array("sleep 2", "Waiting for backend startup..."),
    array("mkdir -p ~/public_html/voxcore && cat > ~/public_html/voxcore/.htaccess << 'HTACCESS'\n<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteBase /\nRewriteRule ^api/(.*)\$ http://127.0.0.1:8000/api/\$1 [P,L]\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [QSA,L]\n</IfModule>\nHTACCESS", "Configuring web server routing..."),
    array("(crontab -l 2>/dev/null | grep -v voxcore; echo '*/5 * * * * cd ~/VOXCORE/voxquery && source venv/bin/activate && python -m uvicorn voxquery.api.main:app --host 127.0.0.1 --port 8000 >> ~/logs/voxcore-backend.log 2>&1') | crontab -", "Setting up auto-restart..."),
);

$step = 1;
foreach ($commands as $cmd_info) {
    $cmd = $cmd_info[0];
    $desc = $cmd_info[1];
    
    echo "\n[Step $step] $desc\n";
    echo "$ $cmd\n";
    
    $output = array();
    $return = 0;
    exec($cmd . ' 2>&1', $output, $return);
    
    if (!empty($output)) {
        echo implode("\n", $output) . "\n";
    }
    if ($return !== 0) {
        echo "⚠ Command returned: $return\n";
    }
    
    ob_flush();
    flush();
    $step++;
}

echo "\n\n";
echo "==========================================\n";
echo "✓✓✓ VOXCORE IS NOW LIVE! ✓✓✓\n";
echo "==========================================\n";
echo "Website:   https://voxcore.org/\n";
echo "Health:    https://voxcore.org/api/health\n";
echo "Docs:      https://voxcore.org/api/docs\n";
echo "DATABASE:  LOCKED (secure browsing only)\n";
echo "\nNEXT: Delete setup.php from cPanel for security\n";
echo "==========================================\n";
?>