/**
 * Stick Figure Canvas Renderer
 * Draws fun big-headed stick figures with user photos
 */

class StickFigureRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.figures = [];
        this.zones = [];
        this.images = {};
        this.animationFrame = null;
        this.time = 0;

        // Colors for zone types
        this.colors = {
            office: '#22c55e',
            restaurant: '#f97316',
            pub: '#a855f7',
            cafe: '#3b82f6',
            gym: '#ef4444',
            unknown: '#6b7280'
        };

        // Zone icons
        this.icons = {
            office: '🏢',
            restaurant: '🍕',
            pub: '🍺',
            cafe: '☕',
            gym: '🏃',
            unknown: '📍'
        };

        this.init();
    }

    init() {
        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.animate();
    }

    resize() {
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        this.canvas.width = rect.width - 48; // Account for padding
        this.canvas.height = 350;
    }

    async loadImage(src) {
        if (this.images[src]) {
            return this.images[src];
        }

        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => {
                this.images[src] = img;
                resolve(img);
            };
            img.onerror = () => {
                resolve(null);
            };
            img.src = src;
        });
    }

    updateData(data) {
        this.figures = [];
        const grouped = data.grouped || {};
        const clusters = data.clusters || [];

        // Calculate positions for each zone group
        let xOffset = 80;
        const zoneTypes = ['office', 'pub', 'restaurant', 'cafe', 'gym', 'unknown'];

        for (const zoneType of zoneTypes) {
            const zoneClusters = grouped[zoneType] || [];
            if (zoneClusters.length === 0) continue;

            // Add zone label
            const zoneLabel = {
                type: 'zone',
                zoneType: zoneType,
                x: xOffset,
                y: 30,
                icon: this.icons[zoneType],
                color: this.colors[zoneType]
            };
            this.figures.push(zoneLabel);

            // Add figures for each cluster in this zone
            let figureX = xOffset;
            for (const cluster of zoneClusters) {
                for (let i = 0; i < cluster.members.length; i++) {
                    const person = cluster.members[i];
                    const figure = {
                        type: 'figure',
                        id: person.id,
                        name: person.name,
                        emoji: person.avatar_emoji || '😀',
                        x: figureX + (i * 70),
                        y: 120,
                        color: this.colors[zoneType],
                        zone: person.current_zone || 'Out & About',
                        animOffset: Math.random() * Math.PI * 2
                    };
                    this.figures.push(figure);
                }

                // If cluster has multiple people, add a "together" indicator
                if (cluster.members.length > 1) {
                    const clusterBubble = {
                        type: 'cluster',
                        x: figureX + ((cluster.members.length - 1) * 35),
                        y: 70,
                        count: cluster.members.length,
                        color: this.colors[zoneType]
                    };
                    this.figures.push(clusterBubble);
                }

                figureX += cluster.members.length * 70 + 40;
            }

            xOffset = figureX + 80;
        }

    }

    animate() {
        this.time += 0.02;
        this.draw();
        this.animationFrame = requestAnimationFrame(() => this.animate());
    }

    draw() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        if (this.figures.length === 0) {
            this.drawEmptyState();
            return;
        }

        // Draw all elements
        for (const item of this.figures) {
            if (item.type === 'zone') {
                this.drawZoneLabel(item);
            } else if (item.type === 'cluster') {
                this.drawClusterBubble(item);
            } else if (item.type === 'figure') {
                this.drawStickFigure(item);
            }
        }
    }

    drawEmptyState() {
        const ctx = this.ctx;
        ctx.fillStyle = '#64748b';
        ctx.font = '600 28px Nunito, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('🏃‍♂️ No one to catch yet...', this.canvas.width / 2, this.canvas.height / 2 - 20);
        ctx.font = '16px Nunito, sans-serif';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('Check in and start the chase!', this.canvas.width / 2, this.canvas.height / 2 + 20);
    }

    drawZoneLabel(item) {
        const ctx = this.ctx;

        // Draw zone icon and label
        ctx.font = '32px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(item.icon, item.x - 20, item.y + 10);

        // Zone name
        ctx.font = 'bold 14px sans-serif';
        ctx.fillStyle = item.color;
        const zoneName = item.zoneType.charAt(0).toUpperCase() + item.zoneType.slice(1);
        ctx.fillText(zoneName, item.x + 20, item.y + 5);

        // Draw a line under the zone
        ctx.beginPath();
        ctx.strokeStyle = item.color;
        ctx.lineWidth = 2;
        ctx.moveTo(item.x - 30, item.y + 25);
        ctx.lineTo(item.x + 200, item.y + 25);
        ctx.stroke();
    }

    drawClusterBubble(item) {
        const ctx = this.ctx;

        // Draw bubble
        ctx.beginPath();
        ctx.arc(item.x, item.y, 25, 0, Math.PI * 2);
        ctx.fillStyle = item.color;
        ctx.fill();

        // Draw count
        ctx.fillStyle = 'white';
        ctx.font = 'bold 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${item.count}`, item.x, item.y);

        // Draw "together" text
        ctx.font = '12px sans-serif';
        ctx.fillStyle = '#94a3b8';
        ctx.fillText('together!', item.x, item.y + 40);
    }

    drawStickFigure(item) {
        const ctx = this.ctx;
        const x = item.x;
        const y = item.y;

        // Add slight bobbing animation
        const bobOffset = Math.sin(this.time * 2.5 + item.animOffset) * 2;
        const armSwing = Math.sin(this.time * 4 + item.animOffset) * 0.3;
        const legSwing = Math.sin(this.time * 3 + item.animOffset) * 0.15;

        ctx.save();
        ctx.translate(x, y + bobOffset);

        // Draw shadow
        ctx.beginPath();
        ctx.ellipse(0, 95, 15, 5, 0, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.fill();

        // Draw body (smaller stick figure)
        ctx.strokeStyle = item.color;
        ctx.lineWidth = 2.5;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // Body (shorter)
        ctx.beginPath();
        ctx.moveTo(0, 22);
        ctx.lineTo(0, 55);
        ctx.stroke();

        // Legs (shorter with animation)
        ctx.beginPath();
        ctx.moveTo(0, 55);
        ctx.lineTo(-12 - legSwing * 10, 90);
        ctx.moveTo(0, 55);
        ctx.lineTo(12 + legSwing * 10, 90);
        ctx.stroke();

        // Arms (shorter with swing animation)
        ctx.beginPath();
        ctx.moveTo(0, 30);
        ctx.lineTo(-18 + armSwing * 15, 50);
        ctx.moveTo(0, 30);
        ctx.lineTo(18 - armSwing * 15, 50);
        ctx.stroke();

        // Head (smaller circle with emoji)
        const headRadius = 22;

        // Draw head glow
        const gradient = ctx.createRadialGradient(0, 0, headRadius - 5, 0, 0, headRadius + 8);
        gradient.addColorStop(0, 'transparent');
        gradient.addColorStop(1, item.color + '20');
        ctx.beginPath();
        ctx.arc(0, 0, headRadius + 8, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Draw head background
        ctx.beginPath();
        ctx.arc(0, 0, headRadius, 0, Math.PI * 2);
        ctx.fillStyle = '#1e293b';
        ctx.fill();

        // Draw emoji avatar
        ctx.font = '24px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(item.emoji, 0, 1);

        // Draw head border
        ctx.beginPath();
        ctx.arc(0, 0, headRadius, 0, Math.PI * 2);
        ctx.strokeStyle = item.color;
        ctx.lineWidth = 3;
        ctx.stroke();

        // Draw name below (first name only for compactness)
        ctx.fillStyle = '#f1f5f9';
        ctx.font = '600 12px Nunito, sans-serif';
        ctx.textAlign = 'center';
        const firstName = item.name.split(' ')[0];
        ctx.fillText(firstName, 0, 110);

        ctx.restore();
    }

    destroy() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }
}

// Export for use in other scripts
window.StickFigureRenderer = StickFigureRenderer;
