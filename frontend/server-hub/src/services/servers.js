import axios from 'axios';

export async function getServerList() {
  return await axios.get('http://localhost:7000/list');
}
