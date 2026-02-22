import TitleMessage from '../components/TitleMessage';
import WaveformVisualizer from '../components/WaveformVisualizer';

export default function MyApp() {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <TitleMessage />
      <WaveformVisualizer />
    </div>
  );
}
