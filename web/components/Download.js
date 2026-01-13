import { Download, Apple, Monitor, Terminal } from "lucide-react";

export default function DownloadCard({ platform }) {
  const configs = {
    macOS: {
      icon: <Apple className="w-10 h-10" />,
      title: "macOS",
      version: "v1.0.0 (Universal)",
      specs: ["macOS Monterey or later", "Apple Silicon & Intel support"],
      link: "https://github.com/ethanmcf/UofTBookingBot/releases/latest/download/macos.dmg",
      color: "bg-black",
    },
    windows: {
      icon: <Monitor className="w-10 h-10" />,
      title: "Windows",
      version: "v1.0.0 (x64)",
      specs: ["Windows 10/11", "Standalone .exe"],
      link: "https://github.com/ethanmcf/UofTBookingBot/releases/latest/download/windows.exe",
      color: "bg-blue-600",
    },
    linux: {
      icon: <Terminal className="w-10 h-10" />,
      title: "Linux",
      version: "v1.0.0 (AppImage)",
      specs: ["Ubuntu, Fedora, Debian", "No installation required"],
      link: "https://github.com/ethanmcf/UofTBookingBot/releases/latest/download/linux.appImage",
      color: "bg-orange-600",
    },
  };

  const data = configs[platform] || configs.windows;

  return (
    <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 flex flex-col items-center text-center">
      {/* Icon Circle */}
      <div
        className={`w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mb-6`}
      >
        <div className="text-gray-800">{data.icon}</div>
      </div>

      <h3 className="font-bold text-2xl mb-1">{data.title}</h3>
      <p className="text-gray-500 text-sm mb-6">{data.version}</p>

      {/* Feature List */}
      <ul className="text-left w-full bg-gray-50 rounded-lg p-4 mb-6 space-y-2">
        {data.specs.map((spec, index) => (
          <li key={index} className="flex items-center text-xs text-gray-600">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
            {spec}
          </li>
        ))}
      </ul>

      {/* Dynamic CTA Button */}
      <a
        href={data.link}
        className={`flex items-center justify-center gap-2 w-full ${data.color} text-white py-3 px-6 rounded-xl font-semibold hover:opacity-90 transition-all shadow-md active:scale-95`}
      >
        <Download size={18} />
        Get for {data.title}
      </a>
    </div>
  );
}
