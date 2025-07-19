# Vessel Maintenance AI System - Frontend

A modern, responsive web interface for the Vessel Maintenance AI System built by Fusionpact Technologies Inc.

## Features

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark/Light Theme**: Toggle between themes with persistent settings
- **Modern Components**: Cards, modals, dropdowns, tooltips, and more
- **Smooth Animations**: CSS transitions and animations for enhanced user experience

### 📊 Dashboard
- **Real-time Statistics**: Critical alerts, processed documents, active vessels
- **Recent Activity Feed**: Latest system activities and notifications
- **Quick Actions**: Fast access to common tasks
- **System Health Monitoring**: Live status indicators

### 🧠 AI Processing
- **Text Input**: Direct text processing with AI analysis
- **File Upload**: Drag & drop support for multiple file formats
- **Real-time Results**: Instant classification and analysis
- **Detailed Output**: Confidence scores, entities, keywords, recommendations

### 📈 Analytics
- **Interactive Charts**: Classification distribution, priority breakdown, trends
- **Time-based Filtering**: View data for different time periods
- **Smart Insights**: AI-generated insights based on data patterns
- **Export Capabilities**: Download reports and data

### 📝 History Management
- **Search & Filter**: Advanced filtering by classification, priority, vessel
- **Pagination**: Efficient browsing of large datasets
- **Detailed Views**: Full document analysis details
- **Export Options**: Download historical data

### ⚙️ Settings & Management
- **System Health Checks**: Monitor API, database, and AI processor status
- **Configuration Viewer**: System settings and parameters
- **Data Management**: Cleanup, export, and sample data loading
- **Notification Settings**: Customize alert preferences

## File Structure

```
frontend/
├── index.html              # Main application HTML
├── css/
│   ├── main.css            # Core styles and layout
│   ├── components.css      # Component-specific styles
│   └── responsive.css      # Mobile and responsive design
├── js/
│   ├── main.js            # Main application logic
│   ├── api.js             # API interface and mock data
│   ├── charts.js          # Data visualization with Chart.js
│   └── components.js      # Reusable UI components
├── images/                # Image assets (placeholder)
├── components/            # Additional component files (placeholder)
└── README.md             # This file
```

## Technologies Used

- **HTML5**: Semantic markup and modern web standards
- **CSS3**: Modern styling with CSS variables and grid/flexbox
- **Vanilla JavaScript**: No frameworks, pure JavaScript for maximum performance
- **Chart.js**: Beautiful, responsive charts and data visualization
- **Font Awesome**: Comprehensive icon library
- **Inter Font**: Modern, readable typography

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- HTTP server (for local development)

### Installation

1. **Clone or download** the frontend files to your local machine

2. **Serve the files** using any HTTP server:
   
   **Using Python:**
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Python 2
   python -m SimpleHTTPServer 8000
   ```
   
   **Using Node.js (http-server):**
   ```bash
   npx http-server -p 8000
   ```
   
   **Using Live Server (VS Code extension):**
   - Install the Live Server extension
   - Right-click on `index.html` and select "Open with Live Server"

3. **Open your browser** and navigate to `http://localhost:8000`

### Backend Integration

The frontend is designed to work with the Vessel Maintenance AI System backend. To connect:

1. Ensure the backend is running (typically on port 5000)
2. The frontend will automatically attempt to connect to the backend API
3. If the backend is unavailable, the frontend will use mock data for demonstration

## Customization

### Themes
- Colors are defined in CSS variables in `css/main.css`
- Modify the `:root` section to change the color scheme
- Dark theme variables are in `[data-theme="dark"]`

### Adding New Features
1. **UI Components**: Add new components to `js/components.js`
2. **API Endpoints**: Extend the API class in `js/api.js`
3. **Charts**: Create new chart types in `js/charts.js`
4. **Styles**: Add component styles to `css/components.css`

### Configuration
Key settings can be modified in `js/main.js`:
- API base URL
- Default theme
- Notification duration
- File upload limits

## Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Performance

- **Lightweight**: No heavy frameworks, minimal dependencies
- **Fast Loading**: Optimized CSS and JavaScript
- **Responsive**: Smooth performance on all devices
- **Caching**: Uses browser caching for static assets

## Security

- **XSS Protection**: All user inputs are properly sanitized
- **CSRF Protection**: Uses secure API communication patterns
- **Content Security**: External resources loaded from trusted CDNs only

## API Integration

The frontend communicates with the backend through these endpoints:

- `POST /process` - Text processing
- `POST /process_file` - File upload and processing
- `GET /analytics` - Analytics data
- `GET /history` - Processing history
- `GET /health` - System health check
- `GET /config` - System configuration
- `POST /cleanup` - Data cleanup
- `GET /export` - Data export

## Troubleshooting

### Common Issues

1. **Blank Page**: Check browser console for JavaScript errors
2. **API Errors**: Verify backend is running and accessible
3. **Styling Issues**: Clear browser cache and reload
4. **Mobile Issues**: Ensure proper viewport meta tag

### Development Tips

1. **Use Browser DevTools**: Essential for debugging and testing
2. **Test Responsive Design**: Use device emulation in DevTools
3. **Monitor Network**: Check API calls in Network tab
4. **Check Console**: Watch for JavaScript errors and warnings

## Contributing

To contribute to the frontend:

1. Follow the existing code style and patterns
2. Test on multiple browsers and devices
3. Ensure responsive design works properly
4. Add comments for complex functionality
5. Update this README if adding new features

## License

Part of the Vessel Maintenance AI System by Fusionpact Technologies Inc.

## Support

For support and questions:
- Check the browser console for error messages
- Verify backend connectivity
- Review the API documentation
- Test with mock data mode