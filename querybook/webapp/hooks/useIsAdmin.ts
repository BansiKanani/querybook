import { useSelector } from 'react-redux';
import { IStoreState } from 'redux/store/types';

/**
 * useIsAdmin - React hook to get current user's admin status from Redux
 * @returns {boolean} true if user is admin, false otherwise
 */
export function useIsAdmin(): boolean {
    return useSelector((state: IStoreState) => !!state.user.myUserInfo?.isAdmin);
}
