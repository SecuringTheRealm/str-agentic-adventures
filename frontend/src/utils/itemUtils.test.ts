import { describe, it, expect } from 'vitest';
import { formatItemValue, getRarityColor, getRarityDisplayName } from './itemUtils';

describe('itemUtils', () => {
  describe('formatItemValue', () => {
    it('formats values correctly', () => {
      expect(formatItemValue(undefined)).toBe('');
      expect(formatItemValue(null as any)).toBe('');
      expect(formatItemValue(0)).toBe('0 gp');
      expect(formatItemValue(50)).toBe('50 cp');
      expect(formatItemValue(100)).toBe('1 gp');
      expect(formatItemValue(150)).toBe('1 gp 50 cp');
      expect(formatItemValue(1500)).toBe('15 gp');
    });
  });

  describe('getRarityColor', () => {
    it('returns correct colors for rarities', () => {
      expect(getRarityColor('common')).toBe('#9CA3AF');
      expect(getRarityColor('uncommon')).toBe('#10B981');
      expect(getRarityColor('rare')).toBe('#3B82F6');
      expect(getRarityColor('very rare')).toBe('#8B5CF6');
      expect(getRarityColor('legendary')).toBe('#F59E0B');
      expect(getRarityColor('artifact')).toBe('#EF4444');
      expect(getRarityColor(undefined)).toBe('#9CA3AF'); // defaults to common
      expect(getRarityColor('invalid')).toBe('#9CA3AF'); // defaults to common
    });
  });

  describe('getRarityDisplayName', () => {
    it('formats rarity names correctly', () => {
      expect(getRarityDisplayName('common')).toBe('Common');
      expect(getRarityDisplayName('very rare')).toBe('Very rare');
      expect(getRarityDisplayName(undefined)).toBe('Common');
    });
  });
});