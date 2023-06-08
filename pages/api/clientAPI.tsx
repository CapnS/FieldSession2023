import { NextApiRequest, NextApiResponse } from 'next';
import logger from '../../utils/logger';

export default (req: NextApiRequest, res: NextApiResponse) => {
  const { message } = req.body;

  if (message) {
    const timestamp = new Date().toISOString();
    logger.info(`Message received at ${timestamp}: ${message}`);
    res.status(200).json({ status: 'Logged' });
  } else {
    res.status(400).json({ error: 'No message provided' });
  }
};
