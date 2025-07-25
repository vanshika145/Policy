import { Brain } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-white py-12">
      <div className="container mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-6 md:mb-0">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">AI Policy Decoder</span>
          </div>

          {/* Navigation */}
          <div className="flex gap-8 mb-6 md:mb-0">
            <a href="#" className="text-gray-300 hover:text-white transition-colors">About</a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors">Contact</a>
            <a href="#" className="text-gray-300 hover:text-white transition-colors">Privacy</a>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-slate-700 mt-8 pt-8 text-center text-gray-400">
          © 2024 AI Policy Decoder. All rights reserved.
        </div>
      </div>
    </footer>
  );
};