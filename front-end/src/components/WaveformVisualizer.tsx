import React, { useState, useMemo, JSX } from 'react';

// STYLES (Tailwind-like inline styles for simplicity)
const styles = {
  container: {
    padding: '2rem',
    fontFamily: 'sans-serif',
    maxWidth: '800px',
    margin: '0 auto',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    borderRadius: '8px',
  },
  controlGroup: {
    marginBottom: '1rem',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '0.5rem',
  },
  label: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '0.9rem',
    fontWeight: 'bold',
    color: '#a0a0a0',
  },
  slider: {
    width: '100%',
    cursor: 'pointer',
  },
  canvasContainer: {
    position: 'relative' as const,
    height: '300px',
    border: '1px solid #333',
    borderRadius: '4px',
    backgroundColor: '#000',
    overflow: 'hidden',
  },
  legend: {
    marginTop: '1rem',
    display: 'flex',
    gap: '1.5rem',
    fontSize: '0.8rem',
    justifyContent: 'center',
  },
  legendItem: (color: string) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    color: color,
  }),
};

const WaveformVisualizer = (): JSX.Element => {
  // --- STATE ---
  // Signal Frequency (Hz): How fast the enemy moves
  const [frequency, setFrequency] = useState(2);
  // Sampling Rate (Hz): How often your scope updates
  const [samplingRate, setSamplingRate] = useState(20);

  // --- CONSTANTS ---
  const DURATION = 2; // Seconds of time to display
  const AMPLITUDE = 80; // Pixel height of wave
  const CENTER_Y = 150; // Vertical center of canvas

  // --- CALCULATIONS ---

  // 1. Generate the "True" Continuous Signal (High Resolution)
  // We use a very high sample rate (1000Hz) to simulate "analog" reality
  const trueSignalPoints = useMemo(() => {
    const points = [];
    const resolution = 1000;
    for (let i = 0; i <= DURATION * resolution; i++) {
      const t = i / resolution;
      const y = CENTER_Y - AMPLITUDE * Math.sin(2 * Math.PI * frequency * t);
      const x = (t / DURATION) * 100; // Map time to 0-100% width
      points.push(`${x}% ${y}px`);
    }
    return points.join(', ');
  }, [frequency]);

  // 2. Generate the "Sampled" Discrete Signal (Your View)
  // These points only exist at T = n / samplingRate
  const sampledPoints = useMemo(() => {
    const points = [];
    const totalSamples = Math.floor(DURATION * samplingRate);

    for (let i = 0; i <= totalSamples; i++) {
      const t = i / samplingRate;
      const y = CENTER_Y - AMPLITUDE * Math.sin(2 * Math.PI * frequency * t);
      const x = (t / DURATION) * 100;

      points.push({ x, y, t });
    }
    return points;
  }, [frequency, samplingRate]);

  // Check for Aliasing (Nyquist Condition: fs < 2*f)
  const isAliasing = samplingRate < 2 * frequency;

  return (
    <div style={styles.container}>
      <h2
        style={{
          borderBottom: '1px solid #444',
          paddingBottom: '0.5rem',
          marginBottom: '1.5rem',
        }}
      >
        Nyquist's Sniper: Scope Prototype
      </h2>

      {/* CONTROLS */}
      <div style={styles.controlGroup}>
        <div style={styles.label}>
          <span>Target Frequency (f)</span>
          <span>{frequency} Hz</span>
        </div>
        <input
          type="range"
          min="0.5"
          max="10"
          step="0.1"
          value={frequency}
          onChange={(e) => setFrequency(parseFloat(e.target.value))}
          style={styles.slider}
        />
      </div>

      <div style={styles.controlGroup}>
        <div style={styles.label}>
          <span>Scope Sampling Rate (fs)</span>
          <span style={{ color: isAliasing ? '#ff4444' : '#4caf50' }}>
            {samplingRate} Hz {isAliasing ? '(ALIASING WARNING)' : '(OK)'}
          </span>
        </div>
        <input
          type="range"
          min="1"
          max="50"
          step="0.5"
          value={samplingRate}
          onChange={(e) => setSamplingRate(parseFloat(e.target.value))}
          style={styles.slider}
        />
      </div>

      {/* VISUALIZER */}
      <div style={styles.canvasContainer}>
        {/* The "Truth" (Analog Signal) */}

        {/* RE-IMPLEMENTATION: Using absolute divs for maximum reliability */}

        {/* 1. The Continuous Line (Approximated with many small divs) */}
        {/* (Skipped for performance in this specific render, focusing on the SVG below) */}
        <svg
          viewBox={`0 0 100 300`}
          preserveAspectRatio="none"
          style={{ width: '100%', height: '100%' }}
        >
          <path
            d={`M ${trueSignalPoints
              .split(', ')
              .map((p) => {
                const [x, y] = p.split(' ');
                return `${x.replace('%', '')} ${y.replace('px', '')}`;
              })
              .join(' L ')}`}
            fill="none"
            stroke="#555"
            strokeWidth="0.5"
          />
        </svg>

        {/* 2. The Samples (Red Dots) */}
        {sampledPoints.map((point, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${point.x}%`,
              top: `${point.y}px`,
              width: '8px',
              height: '8px',
              backgroundColor: '#ff4444',
              borderRadius: '50%',
              transform: 'translate(-50%, -50%)',
              boxShadow: '0 0 4px #ff0000',
              transition: 'top 0.1s linear', // Smooth out slight jitters
            }}
          />
        ))}

        {/* 3. The "Reconstructed" Path (Visualizing the Aliasing) */}
        <svg
          viewBox={`0 0 100 300`}
          preserveAspectRatio="none"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
          }}
        >
          <path
            d={`M ${sampledPoints.map((p) => `${p.x} ${p.y}`).join(' L ')}`}
            fill="none"
            stroke="#ff4444"
            strokeWidth="2"
            strokeDasharray="4"
            opacity="0.5"
          />
        </svg>
      </div>

      <div style={styles.legend}>
        <div style={styles.legendItem('#555')}>── Real Signal (Truth)</div>
        <div style={styles.legendItem('#ff4444')}>●--● Sampled Signal (Scope)</div>
      </div>
    </div>
  );
};

export default WaveformVisualizer;
