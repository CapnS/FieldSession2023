import winston from 'winston';

// Create a new Winston logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: 'logfile.log' })
  ]
});

function logUserName(name: string) {
    logger.info(`User logged in: ${name}`);
  }
  
export default logger;
