// Digital Complaint Management System - HTML5 Canvas Reporting Engine

function adjustColorBrightness(hex, percent) {
    let R = parseInt(hex.substring(1, 3), 16);
    let G = parseInt(hex.substring(3, 5), 16);
    let B = parseInt(hex.substring(5, 7), 16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R < 255) ? R : 255;
    G = (G < 255) ? G : 255;
    B = (B < 255) ? B : 255;

    R = (R > 0) ? R : 0;
    G = (G > 0) ? G : 0;
    B = (B > 0) ? B : 0;

    const rHex = R.toString(16).padStart(2, '0');
    const gHex = G.toString(16).padStart(2, '0');
    const bHex = B.toString(16).padStart(2, '0');

    return `#${rHex}${gHex}${bHex}`;
}

function drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height);
    ctx.lineTo(x, y + height);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
}

function drawBarChart(canvasId, chartData, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    // Make responsive to container size
    const parent = canvas.parentElement;
    const width = parent.clientWidth;
    const height = parent.clientHeight || 280;
    canvas.width = width;
    canvas.height = height;
    
    const keys = Object.keys(chartData);
    const values = Object.values(chartData).map(Number);
    
    if (keys.length === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No data available to display', width/2, height/2);
        return;
    }
    
    const maxVal = Math.max(...values, 5); // Minimum peak scale of 5
    const padding = 50;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    // Bar dimensions
    const barSpacingRatio = 0.4;
    const sectionWidth = chartWidth / keys.length;
    const barWidth = sectionWidth * (1 - barSpacingRatio);
    const barSpacing = sectionWidth * barSpacingRatio;
    
    // Draw Axis lines
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Y-Axis Gridlines & labels
    const gridCount = 5;
    ctx.fillStyle = '#64748b';
    ctx.font = '10px Inter';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i <= gridCount; i++) {
        const val = Math.round((maxVal / gridCount) * i);
        const y = height - padding - (chartHeight / gridCount) * i;
        ctx.fillText(val, padding - 10, y);
        
        ctx.strokeStyle = '#f1f5f9';
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Draw bars
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    
    keys.forEach((key, idx) => {
        const val = values[idx];
        const barHeight = (val / maxVal) * chartHeight;
        const x = padding + barSpacing/2 + idx * (barWidth + barSpacing);
        const y = height - padding - barHeight;
        
        // Gradient fill
        const color = colors[idx % colors.length] || '#3b82f6';
        const grad = ctx.createLinearGradient(x, y, x, height - padding);
        grad.addColorStop(0, color);
        grad.addColorStop(1, adjustColorBrightness(color, -20));
        
        ctx.fillStyle = grad;
        // Drawing slightly rounded top corners
        if (barHeight > 6) {
            drawRoundedRect(ctx, x, y, barWidth, barHeight, 6);
        } else {
            ctx.fillRect(x, y, barWidth, barHeight);
        }
        ctx.fill();
        
        // Draw numeric value labels on top of bar
        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 11px Inter';
        ctx.fillText(val, x + barWidth/2, y - 18);
        
        // Draw horizontal label description
        ctx.fillStyle = '#64748b';
        ctx.font = '10px Inter';
        let label = key;
        if (label.length > 12) label = label.substring(0, 10) + '..';
        ctx.fillText(label, x + barWidth/2, height - padding + 10);
    });
}

function drawPieChart(canvasId, chartData, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const parent = canvas.parentElement;
    const width = parent.clientWidth;
    const height = parent.clientHeight || 280;
    canvas.width = width;
    canvas.height = height;
    
    const keys = Object.keys(chartData);
    const values = Object.values(chartData).map(Number);
    const total = values.reduce((a, b) => a + b, 0);
    
    if (total === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No data available to display', width/2, height/2);
        return;
    }
    
    // Placement
    const isMobile = width < 480;
    const centerX = isMobile ? width / 2 : width * 0.35;
    const centerY = isMobile ? height * 0.4 : height / 2;
    const radius = Math.min(centerX, centerY) * 0.75;
    
    let startAngle = -0.5 * Math.PI; // Top start
    
    keys.forEach((key, idx) => {
        const val = values[idx];
        const sliceAngle = (val / total) * 2 * Math.PI;
        const endAngle = startAngle + sliceAngle;
        
        ctx.fillStyle = colors[idx % colors.length] || '#3b82f6';
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.closePath();
        ctx.fill();
        
        // Draw slice borders
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        startAngle = endAngle;
    });
    
    // Draw Legend
    const legendX = isMobile ? 20 : width * 0.68;
    let legendY = isMobile ? height * 0.75 : height / 2 - (keys.length * 22) / 2;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.font = '12px Inter';
    
    keys.forEach((key, idx) => {
        const percentage = Math.round((values[idx] / total) * 100);
        ctx.fillStyle = colors[idx % colors.length] || '#3b82f6';
        ctx.fillRect(legendX, legendY - 6, 12, 12);
        
        ctx.fillStyle = '#0f172a';
        ctx.fillText(`${key} (${values[idx]} - ${percentage}%)`, legendX + 20, legendY);
        legendY += isMobile ? 18 : 22;
    });
}

function drawLineChart(canvasId, chartData, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const parent = canvas.parentElement;
    const width = parent.clientWidth;
    const height = parent.clientHeight || 280;
    canvas.width = width;
    canvas.height = height;
    
    const keys = Object.keys(chartData);
    const values = Object.values(chartData).map(Number);
    
    if (keys.length === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No data available', width/2, height/2);
        return;
    }
    
    const maxVal = Math.max(...values, 5);
    const padding = 50;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    // Draw Axis
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();
    
    // Y-Axis Gridlines
    const gridCount = 5;
    ctx.fillStyle = '#64748b';
    ctx.font = '10px Inter';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i <= gridCount; i++) {
        const val = Math.round((maxVal / gridCount) * i);
        const y = height - padding - (chartHeight / gridCount) * i;
        ctx.fillText(val, padding - 10, y);
        
        ctx.strokeStyle = '#f1f5f9';
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Map data points
    const points = [];
    const stepX = keys.length > 1 ? chartWidth / (keys.length - 1) : chartWidth;
    
    keys.forEach((key, idx) => {
        const val = values[idx];
        const x = padding + idx * stepX;
        const y = height - padding - (val / maxVal) * chartHeight;
        points.push({ x, y, val, key });
    });
    
    // Draw continuous path
    ctx.strokeStyle = color || '#3b82f6';
    ctx.lineWidth = 3;
    ctx.beginPath();
    points.forEach((pt, idx) => {
        if (idx === 0) {
            ctx.moveTo(pt.x, pt.y);
        } else {
            ctx.lineTo(pt.x, pt.y);
        }
    });
    ctx.stroke();
    
    // Fill background opacity under the line
    if (points.length > 0) {
        ctx.fillStyle = 'rgba(59, 130, 246, 0.08)';
        ctx.beginPath();
        ctx.moveTo(points[0].x, height - padding);
        points.forEach(pt => ctx.lineTo(pt.x, pt.y));
        ctx.lineTo(points[points.length - 1].x, height - padding);
        ctx.closePath();
        ctx.fill();
    }
    
    // Draw circles and numerical label values
    ctx.textAlign = 'center';
    points.forEach(pt => {
        // Point node
        ctx.fillStyle = color || '#3b82f6';
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 5, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 2, 0, 2 * Math.PI);
        ctx.fill();
        
        // Draw quantity text label
        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 10px Inter';
        ctx.fillText(pt.val, pt.x, pt.y - 12);
        
        // Draw horizontal month title labels
        ctx.fillStyle = '#64748b';
        ctx.font = '10px Inter';
        ctx.fillText(pt.key, pt.x, height - padding + 15);
    });
}
